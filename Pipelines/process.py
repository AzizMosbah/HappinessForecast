import pandas as pd
from Pipelines.config_pipelines import sex_list, predictors_wave_1, wave_1_gam, wave_1_gbm, wave_1_rf, TRAIN_PATH
import h2o
from h2o.estimators import H2OGradientBoostingEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator
from h2o.grid.grid_search import H2OGridSearch
from pygam import LinearGAM, GAM, s, f, te, l
import numpy as np


def process_raw(path: str):
    df = pd.read_csv(path)
    return df


def take_difference(df: pd.DataFrame, sex_list = sex_list):

    df = df.rename(columns={
        'Intergalactic Development Index (IDI), female, Rank': 'Intergalactic Development Index (IDI), Rank, female',
        'Intergalactic Development Index (IDI), male, Rank': 'Intergalactic Development Index (IDI), Rank, male'})
    for i in range(0, len(sex_list), 2):
        label = sex_list[i].split(', male')[0]
        df.loc[:, 'diff - {0}'.format(label)] = df.loc[:, sex_list[i]] - df.loc[:, sex_list[i + 1]]

    df = df.drop(columns=sex_list)

    return df


def take_population_rates(df: pd.DataFrame):

    df.loc[:, 'Population, ages 15–64 (rate)'] = df['Population, ages 15–64 (millions)']/df['Population, total (millions)']
    df.loc[:, 'Population, ages 65 and older (rate)'] = df['Population, ages 65 and older (millions)']/df['Population, total (millions)']
    df.loc[:, 'Population, under age 5 (rate)'] = df['Population, under age 5 (millions)']/df['Population, total (millions)']

    df = df.drop(columns=['Population, ages 15–64 (millions)', 'Population, ages 65 and older (millions)', 'Population, under age 5 (millions)'])

    return df


def loose_correlated_vars(df_: pd.DataFrame, threshold=0.75):
    df = process_raw(TRAIN_PATH).pipe(take_difference).pipe(take_population_rates)
    corr = df.loc[:, (df.columns != 'galactic year') & (df.columns != 'galaxy') & (df.columns != 'y')].corr()
    clean = corr.columns[[sum(df[col].isna())/len(df) < 0.15 for col in corr.columns]]
    unclean = corr.columns[[sum(df[col].isna())/len(df) >= 0.15 for col in corr.columns]]
    to_remove = abs(corr.loc[:, clean]) > threshold
    to_remove = to_remove.loc[unclean]
    to_remove['to keep'] = [sum(to_remove.iloc[i]) < 2 for i in range(len(to_remove))]
    df_ = df_.drop(columns=to_remove[~to_remove['to keep']].index)
    return df_


def h2o_gbm(df: pd.DataFrame, targets: list, predictors: list):

    df_predicted = process_raw(TRAIN_PATH).pipe(take_difference).pipe(take_population_rates).pipe(loose_correlated_vars)

    df_predictors1 = df.dropna(subset=predictors)

    for TARGET in targets:

        df_predictors = df_predicted.loc[:, predictors + [TARGET]]

        index_to_predict = np.array(df_predictors1[TARGET].isna())

        test_df = df_predictors1.loc[index_to_predict, predictors]

        df_predictors = df_predictors.dropna()

        train = h2o.H2OFrame(df_predictors)

        test = h2o.H2OFrame(test_df)

        response = TARGET

        hyper_params_tune = {'max_depth': list(range(1, 21, 1)),
                             'sample_rate': [x / 100. for x in range(20, 101)],
                             'col_sample_rate': [x / 100. for x in range(20, 101)],
                             'col_sample_rate_per_tree': [x / 100. for x in range(20, 101)],
                             'col_sample_rate_change_per_level': [x / 100. for x in range(90, 111)],
                             'min_rows': [1, 2, 4, 8, 16, 25],
                             'nbins': [2 ** x for x in range(4, 9)],
                             'nbins_cats': [2 ** x for x in range(4, 9)],
                             'min_split_improvement': [0, 1e-8, 1e-6, 1e-4],
                             'histogram_type': ["UniformAdaptive", "QuantilesGlobal", "RoundRobin"]}

        search_criteria_tune = {'strategy': "RandomDiscrete",
                                'max_runtime_secs': 5,  ## limit the runtime to 60 minutes
                                'max_models': 100,  ## build no more than 100 models
                                'seed': 1234,
                                'stopping_rounds': 5,
                                'stopping_metric': "rmse",
                                'stopping_tolerance': 1e-3
                                }

        h2ogbm = H2OGradientBoostingEstimator(nfolds=5,
                                              learn_rate=0.05,
                                              learn_rate_annealing=0.99,
                                              score_tree_interval=10,
                                              stopping_rounds=5,
                                              stopping_metric="rmse",
                                              stopping_tolerance=1e-4,
                                              ntrees=1000,
                                              seed=1111,
                                              keep_cross_validation_predictions=True,
                                              distribution='gaussian')

        h2ogbm = H2OGridSearch(h2ogbm, grid_id='gbm_.{0}'.format(TARGET), hyper_params=hyper_params_tune,
                               search_criteria=search_criteria_tune)

        h2ogbm.train(x=predictors, y=response, training_frame=train, seed=1111)

        gbm_gridperf1 = h2ogbm.get_grid(sort_by='rmse', decreasing=False)

        bestgbm = gbm_gridperf1.models[0]

        pred = h2o.as_list(bestgbm.predict(test.drop(len(predictors))), use_pandas=True)

        df_predictors1.loc[index_to_predict, TARGET] = pred.values

        df = df.set_index(['galaxy', 'galactic year']).fillna(
                df_predictors1.set_index(['galaxy', 'galactic year'])).reset_index()

        h2o.remove_all()

    return df


def h2o_drf(df: pd.DataFrame, targets: list, predictors: list):

    df_predicted = process_raw(TRAIN_PATH).pipe(take_difference).pipe(take_population_rates).pipe(loose_correlated_vars)

    df_predictors1 = df.dropna(subset=predictors)

    for TARGET in targets:
        df_predictors = df_predicted.loc[:, predictors + [TARGET]]


        index_to_predict = np.array(df_predictors1[TARGET].isna())

        test_df = df_predictors1.loc[index_to_predict, predictors]

        df_predictors = df_predictors.dropna()

        train = h2o.H2OFrame(df_predictors)

        test = h2o.H2OFrame(test_df)

        response = TARGET

        hyper_params_tune = {
            'max_depth': list(range(5, 60, 1)),
            'nbins': [2 ** x for x in range(4, 9)],
            'nbins_cats': [2 ** x for x in range(4, 9)],
            'ntrees': [100, 200, 400, 800, 1000],
            'histogram_type': ["UniformAdaptive", "QuantilesGlobal", "RoundRobin"]}

        search_criteria_tune = {'strategy': "RandomDiscrete",
                                'max_runtime_secs': 5,  ## limit the runtime to 60 minutes
                                'max_models': 100,  ## build no more than 100 models
                                'seed': 1234,
                                'stopping_rounds': 5,
                                'stopping_metric': "rmse",
                                'stopping_tolerance': 1e-3
                                }

        rf_v1 = H2ORandomForestEstimator(model_id="rf_covType_v1")

        h2orf = H2OGridSearch(rf_v1, grid_id='gbm_.{0}'.format(TARGET), hyper_params=hyper_params_tune,
                              search_criteria=search_criteria_tune)

        h2orf.train(x=predictors, y=response, training_frame=train, seed=1111)

        rf_gridperf1 = h2orf.get_grid(sort_by='mse', decreasing=False)

        bestrf = rf_gridperf1.models[0]

        pred = h2o.as_list(bestrf.predict(test.drop(len(predictors))), use_pandas=True)

        df_predictors1.loc[index_to_predict, TARGET] = pred.values

        df = df.set_index(['galaxy', 'galactic year']).fillna(
                df_predictors1.set_index(['galaxy', 'galactic year'])).reset_index()

        h2o.remove_all()

    return df


def gam_wave_1(df):

    df_predicted = process_raw(TRAIN_PATH).pipe(take_difference).pipe(take_population_rates).pipe(loose_correlated_vars)
    galaxy_to_int = dict((i, g) for g, i in enumerate(df_predicted.galaxy.unique()))
    int_to_galaxy = {v: k for k, v in galaxy_to_int.items()}

    df_predicted.loc[:, ['galaxy']] = [galaxy_to_int[i] for i in df_predicted.galaxy]

    df_predictors1 = df.loc[:, predictors_wave_1]
    df_predictors1 = df_predictors1.dropna()

    for TARGET in wave_1_gam:
        df_predictors = df_predicted.loc[:, predictors_wave_1 + [TARGET]]

        df_predictors = df_predictors.dropna()

        X = df_predictors.loc[:, df_predictors.columns != TARGET]
        y = df_predictors.loc[:, TARGET]

        lams = np.exp(np.random.random(size=(50, 8)) * 6 - 3)

        gam = LinearGAM(s(0, dtype='categorical', by=1) + f(0) + s(1) + s(2) + s(3) + s(4) + s(5) + s(6)).gridsearch(
            np.array(X), np.array(y), lam=lams)

        df_predictors1.loc[:, ['galaxy']] = [galaxy_to_int[i] for i in df_predictors1.galaxy]

        df_predictors1[TARGET] = gam.predict(df_predictors1)

        df_predictors1.loc[:, ['galaxy']] = [int_to_galaxy[i] for i in df_predictors1.galaxy]

        df = df.set_index(['galaxy', 'galactic year']).fillna(
                df_predictors1.set_index(['galaxy', 'galactic year'])).reset_index()

    return df


def imputation_wave_1(df: pd.DataFrame):

        h2o.init(nthreads=-1, min_mem_size='100G', max_mem_size='200G')
        df = df.pipe(h2o_gbm,  wave_1_gbm, predictors_wave_1).pipe(h2o_drf,  wave_1_rf, predictors_wave_1).pipe(gam_wave_1)
        h2o.shutdown()

        return df
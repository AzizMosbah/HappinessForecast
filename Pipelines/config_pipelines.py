TRAIN_PATH = "../train.csv"
TEST_PATH = "../../test.csv"

sex_list = [

    'Life expectancy at birth, male (galactic years)',
    'Life expectancy at birth, female (galactic years)',

    'Mortality rate, male grown up (per 1,000 people)',
    'Mortality rate, female grown up (per 1,000 people)',

    'Labour force participation rate (% ages 15 and older), male',
    'Labour force participation rate (% ages 15 and older), female',

    'Mean years of education, male (galactic years)',
    'Mean years of education, female (galactic years)',

    'Expected years of education, male (galactic years)',
    'Expected years of education, female (galactic years)',

    'Estimated gross galactic income per capita, male',
    'Estimated gross galactic income per capita, female',

    'Population with at least some secondary education, male (% ages 25 and older)',
    'Population with at least some secondary education, female (% ages 25 and older)',

    'Intergalactic Development Index (IDI), male',
    'Intergalactic Development Index (IDI), female',

    'Intergalactic Development Index (IDI), Rank, male',
    'Intergalactic Development Index (IDI), Rank, female',
]

predictors_wave_0_0 = ['galaxy', 'galactic year',
                       'existence expectancy index', 'Gross income per capita', 'Income Index']

wave_0_0_gam = ['Expected years of education (galactic years)']

predictors_wave_0_1 = ['galaxy', 'galactic year', 'existence expectancy index', 'Gross income per capita',
                       'Income Index', 'Expected years of education (galactic years)']

wave_0_1_gam = ['Mean years of education (galactic years)', 'Intergalactic Development Index (IDI), Rank',
                'Jungle area (% of total land area)']

predictors_wave_1 = [
                     'galaxy', 'galactic year', 'existence expectancy index', 'Gross income per capita',
                     'Income Index', 'Expected years of education (galactic years)',
                     'Mean years of education (galactic years)',
                     'Intergalactic Development Index (IDI), Rank'
                      ]

wave_1_gbm = ['Population, urban (%)',
              'Old age dependency ratio (old age (65 and older) per 100 creatures (ages 15-64))',
              'Adolescent birth rate (births per 1,000 female creatures ages 15-19)',
              'Infants lacking immunization, red hot disease (% of one-galactic year-olds)',
              'Gross galactic product (GGP) per capita',
              'Natural resource depletion',
              'Renewable energy consumption (% of total final energy consumption)',
              'Respiratory disease incidence (per 100,000 people)',
              'Interstellar Data Net users, total (% of population)',
              'Gender Development Index (GDI)',
              'Unemployment, total (% of labour force)',
              'Unemployment, youth (% ages 15–24)',
              'Adjusted net savings ',
              'Gross capital formation (% of GGP)',
              'diff - Expected years of education',
              'diff - Life expectancy at birth', 'Population, ages 15–64 (rate)',
              'Exports and imports (% of GGP)',
              'Share of seats in senate (% held by female)',
              'diff - Population with at least some secondary education',
              'Creature Immunodeficiency Disease prevalence, adult (% ages 15-49), total'
              ]

wave_1_gam = ['Domestic credit provided by financial sector (% of GGP)',
              'Gross enrolment ratio, primary (% of primary under-age population)',
              'Intergalactic inbound tourists (thousands)',
              'diff - Intergalactic Development Index (IDI)',
              'diff - Intergalactic Development Index (IDI), Rank'
              ]

wave_1_rf = [
             'Infants lacking immunization, Combination Vaccine (% of one-galactic year-olds)',
             'Outer Galaxies direct investment, net inflows (% of GGP)', 'diff - Mortality rate'
            ]

wave_1_cv_rf = [
    'Population, total (millions)',
    # {'max_depth': 5, 'max_features': 'auto', 'n_estimators': 200}
    'Gross galactic product (GGP), total',
    # {'max_depth': 5, 'max_features': 'auto', 'n_estimators': 800}
    'Total unemployment rate (female to male ratio)',
    # {'max_depth': 40, 'max_features': 'auto', 'n_estimators': 800}
    'diff - Mean years of education',
    # {'max_depth': 20, 'max_features': 'sqrt', 'n_estimators': 800}
    'diff - Estimated gross galactic income per capita'
    # {'max_depth': 5, 'max_features': 'auto', 'n_estimators': 800}
    ]

import numpy as np
import pandas as pd
import tulipy as ti

from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


def performance_indicators(df, period):
    # generate the performance indicators
    data = df.astype('float64')
    rsi = ti.rsi(data['day_close'].values, period)
    rsi = np.insert(rsi, 0, [np.nan for i in range(period)])

    wma = ti.wma(data['day_close'].values, period=period)
    wma = np.insert(wma, 0, [np.nan for i in range(period-1)])

    vwma = ti.vwma(close=data['day_close'].values, volume=data['day_volume'].values, period=period)
    vwma = np.insert(vwma, 0, [np.nan for i in range(period-1)])

    willr = ti.willr(
        high=data['day_high'].values, low=data['day_low'].values, close=data['day_close'].values,
        period=period)
    willr = np.insert(willr, 0, [np.nan for i in range(period-1)])

    stddev = ti.stddev(data['day_close'].values, period=period)
    stddev = np.insert(stddev, 0, [np.nan for i in range(period-1)])

    # set the performance indicator data
    df[f'{period}days_rsi'] = rsi
    df[f'{period}days_wma'] = wma
    df[f'{period}days_vwma'] = vwma
    df[f'{period}days_willr'] = willr
    df[f'{period}days_stddev'] = stddev
    return df


symbol = 'AAPL'
days_back = 120
days_predicted = 30
model_name = 'LSTM_AAPL_LB120_FD30_E5_F50_S30'

# read data
dataframe = pd.read_csv('../data-dumps/stocks_history.csv', index_col="date", parse_dates=True)
dataframe = dataframe.sort_values('date')

# select the symbol and get the last `days_back` close data
df = dataframe[dataframe['symbol'] == symbol]
df = df[['day_open', 'day_high', 'day_low', 'day_close', 'day_volume']]

# get indicators
for i in [5, 10, 15, 20, 25, 30]:
    df = performance_indicators(df, i)
df.dropna(inplace=True)

# drop data
df = df.tail(days_back + days_predicted)
expected = df['day_close'].tail(days_predicted).values
df = df.head(days_back)

# reshape & scale the array
scl = MinMaxScaler()
array = df.values.reshape(df.shape)
array_close = df['day_close'].values.reshape(df.shape[0], 1)

array = scl.fit_transform(array)
array_close = scl.fit_transform(array_close)

# load the model
model = load_model(f'./models/{model_name}.h5')

# predict with the test data
data = np.array([array, ])
Xt = model.predict(data)

# show the predicted value, it shows ten days:
print(np.round(scl.inverse_transform(Xt)[0], 2))
print(expected)

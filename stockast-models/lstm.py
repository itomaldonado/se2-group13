import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

from keras.models import load_model
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


symbol = 'AAPL'

# read data
dataframe = pd.read_csv('../data-dumps/stocks_history.csv', index_col="date", parse_dates=True)
dataframe = dataframe.sort_values('date')

# select symbols and print
df_aapl = dataframe[dataframe['symbol'] == 'AAPL']
df_goog = dataframe[dataframe['symbol'] == 'GOOG']
df_tsla = dataframe[dataframe['symbol'] == 'TSLA']
df_amzn = dataframe[dataframe['symbol'] == 'AMZN']
df = dataframe[dataframe['symbol'] == symbol]

########################################################################
# LSTM
########################################################################
num_periods = 20
look_back = 40
forward_days = 10

# grab just the close
df = df_aapl['day_close']

# reshape the array
array = df.values.reshape(df.shape[0], 1)

# scale it
scl = MinMaxScaler()
array = scl.fit_transform(array)

# split in Train and Test
division = len(array) - (num_periods * forward_days)
array_test = array[division - look_back:]
array_train = array[:division]


# Get the data and splits in input X and output Y, by spliting in `n` past days as input X
# and `m` coming days as Y.
def processData(data, look_back, forward_days, jump=1):
    X, Y = [], []
    for i in range(0, len(data) - look_back - forward_days + 1, jump):
        X.append(data[i:(i+look_back)])
        Y.append(data[(i+look_back):(i+look_back+forward_days)])
    return np.array(X), np.array(Y)


X_test, y_test = processData(array_test, look_back, forward_days, forward_days)
y_test = np.array([list(a.ravel()) for a in y_test])
print(f'Y shape: {y_test.shape}')

X, y = processData(array_train, look_back, forward_days)
y = np.array([list(a.ravel()) for a in y])

X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.20, random_state=42)

# create or *load* a model
NUM_NEURONS_FirstLayer = 50
NUM_NEURONS_SecondLayer = 30
EPOCHS = 50

file_name = (
    f'./models/LSTM_{symbol}_LB{look_back}_FD{forward_days}'
    f'_E{EPOCHS}_F{NUM_NEURONS_FirstLayer}_S{NUM_NEURONS_SecondLayer}.h5'
)

# build the model if no-one exists
if os.path.exists(file_name):
    model = load_model(file_name)
else:
    model = Sequential()
    model.add(LSTM(NUM_NEURONS_FirstLayer, input_shape=(look_back, 1), return_sequences=True))
    model.add(LSTM(NUM_NEURONS_SecondLayer, input_shape=(NUM_NEURONS_FirstLayer, 1)))
    model.add(Dense(forward_days))
    model.compile(loss='mean_squared_error', optimizer='adam')

    history = model.fit(
        X_train, y_train, epochs=EPOCHS,
        validation_data=(X_validate, y_validate),
        shuffle=True, batch_size=2, verbose=2
    )

    plt.figure(figsize=(15, 10))
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.legend(loc='best')
    plt.show()

    # saving the model
    model.save(file_name)
    print(f'Saved model `{file_name}` to disk')


# predict with the test data
Xt = model.predict(X_test)
print(f'Shape: {X_test.shape}')

plt.figure(figsize=(15, 10))
for i in range(0, len(Xt)):
    plt.plot(
        [x + i*forward_days for x in range(len(Xt[i]))],
        scl.inverse_transform(Xt[i].reshape(-1, 1)),
        color='r'
    )
# only to place the label
plt.plot(0, scl.inverse_transform(Xt[i].reshape(-1, 1))[0], color='r', label='Prediction')
plt.plot(scl.inverse_transform(y_test.reshape(-1, 1)), label='Target')
plt.legend(loc='best')
plt.show()

# predict with all the data and see how it reacts

division = len(array) - num_periods*forward_days
leftover = division % forward_days + 1
array_test = array[division-look_back:]
array_train = array[leftover:division]
Xtrain, ytrain = processData(array_train, look_back, forward_days, forward_days)
Xtest, ytest = processData(array_test, look_back, forward_days, forward_days)
Xtrain = model.predict(Xtrain)
Xtrain = Xtrain.ravel()

Xtest = model.predict(Xtest)
Xtest = Xtest.ravel()
y = np.concatenate((ytrain, ytest), axis=0)


plt.figure(figsize=(15, 10))
# Data in Train/Validation
plt.plot(
    [x for x in range(look_back + leftover, len(Xtrain) + look_back + leftover)],
    scl.inverse_transform(Xtrain.reshape(-1, 1)),
    color='r',
    label='Train'
)

# data in Test
plt.plot(
    [x for x in range(
        look_back + leftover + len(Xtrain), len(Xtrain) + len(Xtest) + look_back + leftover)],
    scl.inverse_transform(Xtest.reshape(-1, 1)),
    color='y',
    label='Test'
)

# data used
plt.plot(
    [x for x in range(look_back + leftover, look_back + leftover + len(Xtrain) + len(Xtest))],
    scl.inverse_transform(y.reshape(-1, 1)),
    color='b',
    label='Target'
)
plt.legend(loc='best')
plt.show()

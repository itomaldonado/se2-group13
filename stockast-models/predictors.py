import pandas as pd
import tulipy as ti


def print_info(indicator):
    print('---------------------')
    print("Type:", indicator.type)
    print("Full Name:", indicator.full_name)
    print("Inputs:", indicator.inputs)
    print("Options:", indicator.options)
    print("Outputs:", indicator.outputs)
    print('---------------------')
    print('')


def calculate_stddev(df, period):
    """ Calculates the Standard Deviation for the period given"""

    # Tail the data-frame to the needed data
    data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
    return ti.stddev(data['day_close'].values, period=float(period))[0]


def calculate_rsi(df, period):
    """ Calculates the RSI for the period given"""

    # Tail the data-frame to the needed data
    data = df.tail(period+1)
    return ti.rsi(data['day_close'].values, period)[0]


def calculate_willr(df, period):
    """ Calculates the Williams %R for the period given"""

    # Tail the data-frame to the needed data
    data = df.tail(period)
    return ti.willr(
        high=data['day_high'].values,
        low=data['day_low'].values,
        close=data['day_close'].values,
        period=period
    )[0]


def calculate_wma(df, period):
    """ Calculates the Weighted Moving Average for the period given"""

    # Tail the data-frame to the needed data
    data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
    return ti.wma(data['day_close'].values, period=float(period))[0]


def calculate_vwma(df, period):
    """ Calculates the Volume Weighted Moving Average for the period given"""

    # Tail the data-frame to the needed data
    data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
    return ti.vwma(
        close=data['day_close'].values,
        volume=data['day_volume'].values,
        period=float(period)
    )[0]


if __name__ == '__main__':

    # print params
    print_info(ti.stddev)
    print_info(ti.rsi)
    print_info(ti.willr)
    print_info(ti.wma)
    print_info(ti.vwma)

    # company symbol
    symbol = 'AAPL'

    # RSI period
    period = 10

    # Read in dataframe
    dataframe = pd.read_csv('../data-dumps/stocks_history.csv', index_col="date", parse_dates=True)
    dataframe.sort_values('date', inplace=True)
    df = dataframe[dataframe['symbol'] == symbol]

    # Print Close Standard Deviation
    print(f'Standard Deviation: {calculate_stddev(df, period)}')

    # Print the RSI
    print(f'RSI: {calculate_rsi(df, period)}')

    # Print the RSI
    print(f'Will %R: {calculate_willr(df, period)}')

    # Print Weighted Moving Average
    print(f'Weighted Moving Average: {calculate_wma(df, period)}')

    # Print Volume Weighted Moving Average
    print(f'Volume Weighted Moving Average: {calculate_vwma(df, period)}')

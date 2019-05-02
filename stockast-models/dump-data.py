import json
import pandas as pd
import requests

from requests.auth import HTTPBasicAuth

base_url = 'https://stockast.itomaldonado.com/api'
auth = HTTPBasicAuth('someone@example.com', '1234')


def dump_data_to_csv(name, json_data, index):
    filename = f'../data-dumps/{name}.csv'
    dataframe = pd.read_json(json.dumps(json_data), orient='records')
    dataframe.set_index(index, inplace=True)
    dataframe.to_csv(filename)
    print(f'Saved data to: {filename}')


if __name__ == '__main__':

    # companies
    resp = requests.get(f'{base_url}/companies', auth=auth)
    print(f'companies Status: {resp.status_code}')
    if resp.status_code == 200:
        dump_data_to_csv('companies', resp.json()['data'], 'symbol')

    # historical-data
    resp = requests.get(f'{base_url}/stocks/history', auth=auth)
    print(f'history Status: {resp.status_code}')
    if resp.status_code == 200:
        dump_data_to_csv('stocks_history', resp.json()['data'], 'date')

    # real-time data
    resp = requests.get(f'{base_url}/stocks/realtime', auth=auth)
    print(f'real-time Status: {resp.status_code}')
    if resp.status_code == 200:
        dump_data_to_csv('stocks_real_time', resp.json()['data'], 'timestamp')

import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import csv
import ssl
from datetime import datetime
from elasticsearch import Elasticsearch
import pytz

def load_model(model_path):
    return joblib.load(model_path)

def load_and_prepare_data(csv_path, columns_to_use):
    data = pd.read_csv(csv_path)
    filtered_data = data[columns_to_use]
    return filtered_data

def classify_data(model, data):
    predictions = model.predict(data)
    return predictions

'''
#
def format_timestamp(timestamp_str):
    # Example: convert '15/03/2023 13:45:30' to ISO 8601 format
    return timestamp_str.replace(" ", "T")
'''
def format_timestamp(timestamp_str):

    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    timezone = pytz.timezone('Etc/GMT-7')
    dt = timezone.localize(dt)

    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

def main():
    model_path = '23_rf.pkl'
    csv_path = 'ens3.csv'
    
    # Columns to be used for prediction / 23 features

    columns_to_use = [
        'pkt_len_var', 'fwd_iat_mean', 'tot_bwd_pkts', 'protocol', 'psh_flag_cnt',
        'bwd_iat_max', 'active_max', 'fwd_pkt_len_mean', 'totlen_fwd_pkts',
        'fwd_header_len', 'bwd_iat_min', 'bwd_pkts_s', 'init_bwd_win_byts',
        'urg_flag_cnt', 'fin_flag_cnt', 'idle_std', 'syn_flag_cnt', 'active_std',
        'fwd_pkts_s', 'fwd_act_data_pkts', 'bwd_iat_tot', 'init_fwd_win_byts',
        'down_up_ratio'
    ]


    # Load model
    model = load_model(model_path)

    data_for_prediction = load_and_prepare_data(csv_path, columns_to_use)

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data_for_prediction)

    predictions = classify_data(model, scaled_data)

    data = pd.read_csv(csv_path)
    predictions = ['Malicious' if pred == 1 else 'Benign' for pred in predictions]

    data['Predictions'] = predictions
    data.to_csv('updated_predictions.csv', index=False)
    '''
    # Displaying the predictions
    for i, pred in enumerate(predictions):
        print(f"Row {i}: Classification - {'Malicious' if pred == 1 else 'Benign'}")
        data = pd.read_csv(csv_path)
        data['Predictions'] = predictions
        data.to_csv('updated_predictions.csv', index=False)
    '''

    es_host = ""  # Use HTTPS if necessary
    api_key = ""

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # konek
    es = Elasticsearch(
        es_host,
        ssl_context=ssl_context,
        headers={"Authorization": f"ApiKey {api_key}"}
    )

    # indeks
    index_name = "thesis"

    mapping = {
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},  # Assuming the column name is 'timestamp'
            # Define other fields here as necessary
        }
      }
    }

    es.indices.create(index=index_name, body=mapping, ignore=400)

    # Buka CSV file
    with open('updated_predictions.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'timestamp' in row:
               row['timestamp'] = format_timestamp(row['timestamp'])
            es.index(index=index_name, document=row)

if __name__ == "__main__":
    main()
    

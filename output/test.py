import pandas as pd
import joblib
import numpy as np

def load_model(model_path):
    """Load the pre-trained Random Forest model."""
    return joblib.load(model_path)

def load_and_prepare_data(csv_path, columns_to_use):
    """Load CSV data and filter for the specified columns."""
    data = pd.read_csv(csv_path)
    return data[columns_to_use]

def classify_data(model, data):
    data_values = data.values  # Convert to numpy array to match training data format
    predictions = model.predict(data_values)
    return predictions

def main():
    model_path = 'rfnew.pkl'
    csv_path = 'ens18.csv'

    # Columns features for prediction
    columns_to_use = [
        'pkt_len_var', 'fwd_iat_mean', 'tot_bwd_pkts', 'protocol', 'rst_flag_cnt',
        'psh_flag_cnt', 'active_max', 'fwd_pkt_len_mean', 'totlen_fwd_pkts',
        'fwd_header_len', 'bwd_iat_min', 'bwd_pkts_s', 'init_bwd_win_byts',
        'fin_flag_cnt', 'idle_std', 'urg_flag_cnt', 'syn_flag_cnt', 'active_std',
        'fwd_pkts_s', 'fwd_act_data_pkts', 'bwd_iat_tot', 'init_fwd_win_byts',
        'down_up_ratio'
    ]

    model = load_model(model_path)
    data = load_and_prepare_data(csv_path, columns_to_use)

    predictions = classify_data(model, data)

    data['Classification'] = classify_data(model, data)

    data.to_csv('predict_data.csv', index=False)
    print("Classification complete. Results saved to 'predict_data.csv'.")

if __name__ == "__main__":
    main()

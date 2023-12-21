import pandas as pd 
from data_preprocess import ref_dataset, train_dataset, feature_dataset, model_dataset
from drift_metrics import classification_performance_report, label_binary_classification
from drift_metrics import data_stability, data_drift
from combine_reports import combine_html
from Send_email import send_email
import os 

import warnings
warnings.filterwarnings("ignore") 

feature_set = ['od_count_3m',
 'zero_balance_count_1m',
 'ratio_ach_credit_amt_90_180',
 'ratio_ach_debit_amt_90_180',
 'stddev_amount_ach_c_1m',
 'distinct_ach_c_txns_100_6m',
 'distinct_mrdc_txns_1m',
 'ratio_debit_credit_1m',
 'ratio_debit_credit_3m',
 'median_running_balance_6m']

path1 = "/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/data/"
path2 = "/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/reports/"

data_params = pd.read_pickle(path1 + "rs2_dataset/data_params.pkl")
transformer = pd.read_pickle(path1 + "rs2_dataset/data_scaler_v2.pkl")




def main(): 
    try: 
        month = "jan"
        month2 = "January"

        df_ref = ref_dataset(feature_set, data_params, transformer)
        x_train = train_dataset()
        feature_data = feature_dataset(month)
        model_data = model_dataset(month)

        stability_report = data_stability(feature_data, df_ref, month)
        drift_report = data_drift(feature_data, df_ref, month)
        label_binary_report = label_binary_classification(model_data, x_train, month)

        file1 = path2 + "model_performance/label_classification_" + month + ".html"
        file2 = path2 + "data_drift/data_drift_" + month+ ".html"
        file3 = path2 + "data_drift/data_stability_"+month+ ".html"

        files = [file1, file2, file3]
        heading1 = "Model Performance"
        heading2 = "Dataset Drift"
        heading3 = "Dataset Stability"
        main_heading = month2+" Report"
        output_file = path2 + 'combined_reports/report_' +month+'.html'  
        headings = [heading1, heading2, heading3]

        email_sender = 'pooja.sharma@novo.co'
        email_password = os.environ.get('EMAIL_PASSWORD')
        email_receiver = 'psharma0880@gmail.com'

        combine_html(files, headings, output_file, main_heading)
        send_email(email_sender, email_password, email_receiver, month)

    except Exception as e:
        print('!! Error in running main :', e)


if __name__ == "__main__": 
    main()






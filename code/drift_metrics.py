import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.tests import * 
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.test_suite import TestSuite
from evidently.test_preset import BinaryClassificationTestPreset, DataStabilityTestPreset
from evidently.options import ColorOptions
from data_preprocess import ref_dataset, train_dataset, feature_dataset, model_dataset
from ks_metric import ksMetric
import warnings
warnings.filterwarnings("ignore") 

path1 = "/Users/pooja/Desktop/GitHub/model_monitoring/data/"
path2 = "/Users/pooja/Desktop/GitHub/model_monitoring/reports/"

color_scheme = ColorOptions(
    primary_color = "#5a86ad",
    fill_color = "#fff4f2",
    zero_line_color = "#016795",
    current_data_color = "#c292a1",
    reference_data_color = "#017b92"
)


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

column_map = ColumnMapping()
column_map.target = 'actual_fpd'
column_map.prediction = 'default_proba'

data_params = pd.read_pickle(path1 + "rs2_dataset/data_params.pkl")
transformer = pd.read_pickle(path1 + "rs2_dataset/data_scaler_v2.pkl")

df_ref = ref_dataset(feature_set, data_params, transformer)
x_train = train_dataset()
feature_data = feature_dataset()
model_data = model_dataset()  

def classification_performance_report(month): 

        column_mapping = ColumnMapping()
        column_mapping.target = 'actual_fpd'
        column_mapping.prediction = 'predicted_fpd'
        column_mapping.numerical_features = None

        classification_performance_report = Report(metrics=[
            ClassificationPreset()
        ],options=[color_scheme])

        classification_performance_report.run(reference_data = x_train, current_data = model_data, column_mapping=column_mapping)
        classification_performance_report.save_html(path2 +"model_performance/classification_"+ month+ ".html")
        return classification_performance_report


def label_binary_classification(month):

        column_mapping = ColumnMapping()
        column_mapping.target = 'actual_fpd'
        column_mapping.prediction = 'predicted_fpd'
        column_mapping.numerical_features = None

        classification_performance = TestSuite(tests=[
            BinaryClassificationTestPreset(stattest='psi'),
        ],options=[color_scheme])

        classification_performance.run(reference_data = x_train, current_data=model_data, column_mapping = column_mapping)
        classification_performance.save_html(path2 + "model_performance/classification_" + month+ ".html")
        return classification_performance


def classification_metric(month): 
    classification_performance = TestSuite(tests=[
            TestRocAuc(),

        ],options=[color_scheme])
    
    classification_performance.run(reference_data = x_train[['actual_fpd','default_proba']], current_data=model_data, column_mapping = column_map)
    classification_performance.save_html(path2 + "model_performance/rocCurve_" + month+ ".html")
    return classification_performance


def customizedKsMetric(month): 
    ksMetric_report = Report(metrics = [
        ksMetric()
    ])

    ksMetric_report.run(reference_data= x_train[['actual_fpd','default_proba']], current_data= model_data, column_mapping=column_map)
    ksMetric_report.save_html(path2 + "model_performance/ksMetric_" + month+ ".html")
    return ksMetric_report
    
    

def data_stability(month): 
        data_stability= TestSuite(tests=[
            DataStabilityTestPreset(),
        ],options=[color_scheme])
        data_stability.run(current_data=feature_data, reference_data = df_ref, column_mapping=None)
        data_stability.save_html(path2 + 'data_drift/data_stability_'+month+'.html')
        return data_stability


def data_drift(month): 
        data_drift_report = Report(metrics=[
                #DataDriftPreset(stattest="ks", stattest_threshold=0.35),  
                DataDriftPreset(stattest="psi", stattest_threshold=0.25),],options=[color_scheme])
        data_drift_report.run(current_data=feature_data, reference_data = df_ref, column_mapping=None)
        # path = "evidently/examples/integrations/streamlit-dashboard/projects/your-project/reports/first/"
        data_drift_report.save_html(path2 + "data_drift/data_drift_" + month + ".html")
        return data_drift_report
    



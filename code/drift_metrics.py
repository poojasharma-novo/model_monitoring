import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.test_suite import TestSuite
from evidently.test_preset import BinaryClassificationTestPreset
from evidently.options import ColorOptions
from evidently.test_preset import DataStabilityTestPreset

color_scheme = ColorOptions()
color_scheme.primary_color = "#5a86ad"
color_scheme.fill_color = "#fff4f2"
color_scheme.zero_line_color = "#016795"
color_scheme.current_data_color = "#c292a1" 
color_scheme.reference_data_color = "#017b92"


path1 = "/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/data/"
path2 = "/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/reports/"
        

def classification_performance_report(df_cur, x_train, month): 

        column_mapping = ColumnMapping()
        column_mapping.target = 'actual_fpd'
        column_mapping.prediction = 'predicted_fpd'
        column_mapping.numerical_features = None

        classification_performance_report = Report(metrics=[
            ClassificationPreset()
        ],options=[color_scheme])

        classification_performance_report.run(reference_data = x_train, current_data = df_cur, column_mapping=column_mapping)
        classification_performance_report.save_html(path2 +"model_performance/classification_"+ month+ ".html")
        return classification_performance_report


def label_binary_classification(df_cur, x_train, month):

        column_mapping = ColumnMapping()
        column_mapping.target = 'actual_fpd'
        column_mapping.prediction = 'predicted_fpd'
        column_mapping.numerical_features = None

        label_binary_classification_performance = TestSuite(tests=[
            BinaryClassificationTestPreset(),
        ],options=[color_scheme])

        label_binary_classification_performance.run(reference_data = x_train, current_data=df_cur, column_mapping = column_mapping)
        label_binary_classification_performance.save_html(path2 + "model_performance/label_classification_" + month+ ".html")
        return label_binary_classification_performance
    

def data_stability(df_cur, df_ref, month): 
        data_stability= TestSuite(tests=[
            DataStabilityTestPreset(),
        ],options=[color_scheme])
        data_stability.run(current_data=df_cur, reference_data = df_ref, column_mapping=None)
        data_stability.save_html(path2 + 'data_drift/data_stability_'+month+'.html')
        return data_stability


def data_drift(df_cur, df_ref, month): 
        data_drift_report = Report(metrics=[DataDriftPreset(stattest='psi'),],options=[color_scheme])
        data_drift_report.run(current_data=df_cur, reference_data = df_ref, column_mapping=None)
        # path = "evidently/examples/integrations/streamlit-dashboard/projects/your-project/reports/first/"
        data_drift_report.save_html(path2 + "data_drift/data_drift_" + month + ".html")
        return data_drift_report
    



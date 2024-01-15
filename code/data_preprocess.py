import sys
import pandas as pd 
sys.path.insert(0, '/Users/pooja/Desktop/GitHub/model_monitoring/conf')
from config import SQLQuery
from queries import rs2_features, fpd_data

path1 = "/Users/pooja/Desktop/GitHub/model_monitoring/data/"
path2 = "/Users/pooja/Desktop/GitHub/model_monitoring/reports/"

data_params = pd.read_pickle(path1 + "rs2_dataset/data_params.pkl")
transformer = pd.read_pickle(path1 + "rs2_dataset/data_scaler_v2.pkl")

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


# preprocessing rs2_feature dataset 
def rs2_preprocess( df, feature_set, data_params, transformer):
        temp = df.copy()
        
        # treat missing values
        temp[feature_set] = temp[feature_set].fillna(data_params.set_index('feature').to_dict()['median'])
        
        # min max capping
        lower_limit = data_params.set_index('feature').loc[feature_set, 'lower_limit']
        upper_limit = data_params.set_index('feature').loc[feature_set, 'upper_limit']
        temp[feature_set] = temp[feature_set].clip(lower_limit, upper_limit, axis=1)
        
        # scale data using the standard scaler object
        temp.reset_index(drop=True, inplace=True)
        temp[feature_set] = pd.DataFrame(transformer.transform(temp[feature_set]), columns=feature_set)
        
        # return processed dataframe
        return temp

# dataset used for the rs2 model
def ref_dataset(feature_set, data_params, transformer): 
    file_ref = 'lending_novo_txn_features_model_postscreen_v2.pkl'
    df_ref = pd.read_pickle(path1+file_ref)
    df_ref = df_ref[feature_set]
    df_ref = rs2_preprocess(df_ref,feature_set, data_params, transformer)
    return df_ref

# dataset used as x_train in rs2 model
def train_dataset(): 
    x_train = pd.read_csv(path1 + "rs2_dataset/x_train.csv")
    x_train = x_train[['predicted_fpd3','fpd_plus_3','proba']]
    x_train.rename(columns={"predicted_fpd3": "predicted_fpd", "fpd_plus_3": "actual_fpd",'proba': 'default_proba'}, inplace=True)
    return x_train

# current rs2_feature dataset
def feature_dataset():
    querySno = SQLQuery('snowflake')
    engine = querySno.engine
    df = querySno(rs2_features)
    df = df[feature_set]
    df = rs2_preprocess(df,feature_set, data_params, transformer)
    return df

# current rs2 fpd dataset 
def model_dataset(): 
    querySno = SQLQuery('snowflake')
    engine = querySno.engine
    df = querySno(fpd_data)
    return df
      
import pandas as pd 
import numpy as np 
import dataclasses
from typing import List
from evidently import ColumnMapping
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import header_text

column_map = ColumnMapping()
column_map.target = 'actual_fpd'
column_map.prediction = 'default_proba'


def ks1(target, prob):
    data = pd.DataFrame()
    data['y'] = target
    data['y'] = data['y'].astype(float)
    data['p'] = prob
    data['y0'] = 1- data['y']
    # data['bucket'] = pd.cut(data['p'], bins = [0.0,0.30,0.39,0.49, 0.58,1] )
    data['bucket'] = pd.qcut(data['p'].rank(method='first'), 5)
    grouped = data.groupby('bucket', as_index=False)
    kstable = pd.DataFrame()
    kstable['min_prob'] = grouped.min()['p']
    kstable['max_prob'] = grouped.max()['p']
    kstable['events'] = grouped.sum()['y']
    kstable['nonevents'] = grouped.sum()['y0']
    kstable = kstable.sort_values(by='min_prob', ascending=False).reset_index(drop=True)
    kstable['event_rate'] = (kstable.events / data['y'].sum()).apply('{0:.2%}'.format)
    kstable['nonevent_rate'] = (kstable['nonevents'] /  data['y0'].sum()).apply('{0:2%}'.format)
    kstable['cum_eventrate'] = (kstable.events / data['y'].sum()).cumsum()
    kstable['cum_noneventrate'] = (kstable.nonevents / data['y0'].sum()).cumsum()
    kstable['KS'] = np.round(kstable['cum_eventrate'] - kstable['cum_noneventrate'], 3) * 100
    kstable['bad_rate'] = (kstable['events'] / (kstable['events'] + kstable['nonevents'])) * 100
    average_event_rate=kstable['events'].sum()/(kstable['events'].sum()+kstable['nonevents'].sum())
    kstable['Lift']=np.round((kstable['bad_rate']/average_event_rate)/100,2)
    # formatting
    kstable['cum_eventrate'] = kstable['cum_eventrate'].apply('{0:.2%}'.format)
    kstable['cum_noneventrate'] = kstable['cum_noneventrate'].apply('{0:.2%}'.format)
    kstable.index = range(1,6)
    kstable.index.rename('Decile', inplace=True)
    pd.set_option('display.max_columns', 9)

    return str(max(kstable['KS'])), str((kstable.index[kstable['KS']==max(kstable['KS'])][0]))

class KsMetricResult(MetricResult): 
    ks_value_cur: float
    ks_value_ref: float 
    ks_decile_cur: int 
    ks_decile_ref: int


class ksMetric(Metric[KsMetricResult]):
    def calculate(self, data: InputData) -> KsMetricResult:
        target_column = column_map.target
        prob_column = column_map.prediction

        reference_df = data.reference_data
        current_df = data.current_data

        # ks value for current data
        ks_value_cur, ks_decile_cur = ks1(current_df[target_column], current_df[prob_column])

        # ks value for reference (if available)
        kstable_reference = None
        if reference_df is not None:
            ks_value_ref, ks_decile_ref = ks1(reference_df[target_column], reference_df[prob_column])

        return KsMetricResult(
            ks_value_cur = ks_value_cur,
            ks_value_ref = ks_value_ref,
            ks_decile_cur = ks_decile_cur,
            ks_decile_ref =  ks_decile_ref,
        )


@default_renderer(wrap_type=ksMetric)
class KSMetricRender(MetricRenderer): 
    def render_json(self, obj:ksMetric) -> dict: 
        result = dataclasses.asdict(obj.get_result())
        return result
    
    def render_html(self, obj:ksMetric) -> List[BaseWidgetInfo]: 
        metric_result = obj.get_result()
        return [
    header_text(label=f"Ks value is {round(metric_result.ks_value_ref,3)} %  at decile {metric_result.ks_decile_ref} (reference)"),
    header_text(label=f"Ks value is {round(metric_result.ks_value_cur,3)} %  at decile {metric_result.ks_decile_cur} (current)")
]

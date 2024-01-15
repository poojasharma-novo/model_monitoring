from bs4 import BeautifulSoup
import os

import datetime
from dateutil.relativedelta import relativedelta

path1 = "/Users/pooja/Desktop/GitHub/model_monitoring/data/"
path2 = "/Users/pooja/Desktop/GitHub/model_monitoring/reports/"

# previous to previous month 
current_date = datetime.date.today()
previous_to_previous_month = current_date - relativedelta(months=2)
month = previous_to_previous_month.strftime("%b")  
month2 = previous_to_previous_month.strftime('%B')

file1 = path2 + "model_performance/classification_" + month + ".html"
file2 = path2 + "model_performance/rocCurve_" + month + ".html"
file3 = path2 + "model_performance/KsMetric_" + month + ".html"
file4 = path2 + "data_drift/data_drift_" + month+ ".html"
file5 = path2 + "data_drift/data_stability_"+month+ ".html"

files = [file1, file2, file3, file4, file5]
heading1 = "Model Performance"
heading2 = "RocAuc Curve"
heading3 = "Ks Metric"
heading4 = "Dataset Drift"
heading5 = "Dataset Stability"
main_heading = month2+" Report"
output_file = path2 + 'combined_reports/report_' +month+'.html'  
headings = [heading1, heading2, heading3, heading4, heading5]

def combine_html():
  with open(output_file, "w") as output:
    output.write("<!DOCTYPE html>\n<html>\n<head>\n")
    output.write('<meta charset="UTF-8">')
    output.write('<title>Combined Report</title>')

    # CSS for centered and highlighted headings
    output.write("""
      <style>
        .highlight {
          text-align: center;
          background-color: #ddd;
          padding: 10px;
          border: 1px solid #ddd;
        }
        .heading {
            text-align: center;
            padding: 10px;
        }
      </style>
    """)
    output.write(f"<h1 class='heading'>{main_heading}</h1>")
    output.write("\n</head>\n<body>\n")

    # Combine contents with styled headings
    for file, heading in zip(files, headings):
      with open(file, "r") as f:
          content = f.read()
          soup = BeautifulSoup(content, "html.parser")

          output.write(f"<h2 class='highlight'>{heading}</h2>")
          output.write(str(soup))
      output.write("\n\n")

    output.write("\n</body>\n</html>")

   

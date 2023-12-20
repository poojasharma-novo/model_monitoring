from bs4 import BeautifulSoup
import os


def combine_html(files, headings, output_file, main_heading):
  with open(output_file, "w") as output:
    output.write("<!DOCTYPE html>\n<html>\n<head>\n")
    output.write('<meta charset="UTF-8">')
    output.write('<title>Combined Report</title>')

    # Define custom CSS for centered and highlighted headings
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
        soup.body.insert_before(
            BeautifulSoup(f"<h2 class='highlight'>{heading}</h2>", "html.parser")
        )
        output.write(str(soup))
      output.write("\n\n")
    output.write("\n</body>\n</html>")



def monthly_report(month,month2): 
    path = '/Users/pooja/Desktop/Pooja/model monitoring/GitHub/model_monitoring/reports/'
    file1 = path + "model_performance/label_classification_" + month + ".html"
    file2 = path + "data_drift/data_drift_" + month+ ".html"
    file3 = path + "data_drift/data_stability_"+month+ ".html"

    heading1 = "Model Performance"
    heading2 = "Dataset Drift"
    heading3 = "Dataset Stability"
    main_heading = month2+" Report"

    output_file = path + 'combined_reports/report_' +month+'.html'  

    files = [file1, file2, file3]
    headings = [heading1, heading2, heading3]

    combine_html(files, headings, output_file, main_heading)

    print(f"Combined HTML files into: {output_file}")



if __name__ == "__main__": 
    month = ['jan','feb','mar','apr','may','jun','jul','aug']
    month2 = ['January','February','March',"April",'May',"June",'July','August']
    for i in range (len(month)): 
       monthly_report(month[i], month2[i])
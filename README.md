# Model Monitoring for RS2 Model

### Code Files:

1. **data_preprocess.py:** Loads and preprocesses datasets for model performance and data drift calculation.

2. **drift_metrics.py:** Contains code to generate reports for data drift and model drift, saving them in the `reports/data_drift` and `reports/model_performance` folders.

3. **queries.py:** Includes queries for downloading datasets to calculate monthly drift in data and model.

4. **combine_reports.py:** Combines three monitoring reports into a single HTML file and saves the monthly report in the `reports/combined_reports` folder.

5. **Send_email.py:** Can be modified to send emails to specific recipients with attached reports on a monthly basis.

### Document for Reference:
[View Document](https://docs.google.com/document/d/1q5Qwv91bOjmw108FmLly7DeIvdPUFMT1ryg8voOMplQ/edit?usp=sharing)

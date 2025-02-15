import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

# Specify the path to your .xlsx file
file_path = '/Users/lameck/Desktop/work_automation/15TH.2.25.xlsx'

# Read the first worksheet of the .xlsx file
data = pd.read_excel(file_path, sheet_name=1)

# Filter the data for entries with "0 days"
zero_days_data = data[data['Days to no Cooking'] == 0]

# Count the number of entries for each "M/TSR Name" with "0 days"
zero_days_counts = zero_days_data['M/TSR Name'].value_counts().to_dict()

# Filter and count for "0-5 days"
zero_to_five_days_data = data[data['Days to no Cooking'] <= 5]
zero_to_five_days_counts = zero_to_five_days_data['M/TSR Name'].value_counts().to_dict()

# Filter and count for "0-3 days"
zero_to_three_days_data = data[data['Days to no Cooking'] <= 3]
zero_to_three_days_counts = zero_to_three_days_data['M/TSR Name'].value_counts().to_dict()

# Filter and count for "0-7 days"
zero_to_seven_days_data = data[data['Days to no Cooking'] <= 7]
zero_to_seven_days_counts = zero_to_seven_days_data['M/TSR Name'].value_counts().to_dict()

@app.route('/')
def show_days_counts():
    return render_template('index.html', 
                           zero_days_counts=zero_days_counts,
                           zero_to_five_days_counts=zero_to_five_days_counts,
                           zero_to_three_days_counts=zero_to_three_days_counts,
                           zero_to_seven_days_counts=zero_to_seven_days_counts)

if __name__ == '__main__':
    app.run(debug=True)
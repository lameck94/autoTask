from flask import Flask, render_template, request, jsonify
import flask as flask
import pandas as pd
import os

app = Flask(__name__)

# Define a global variable to store the uploaded file path
uploaded_file_path = None

@app.route('/')
def show_days_counts():
    if uploaded_file_path:
        data = pd.read_excel(uploaded_file_path, sheet_name=1)
        # Get all unique M/TSR Names
        all_mtsr_names = data['M/TSR Name'].unique()

        # Prepare a dictionary to hold customer info for each M/TSR Name
        customer_info = data.groupby('M/TSR Name').apply(lambda x: x[['Customer Name', 'Customer ID']].to_dict('records')).to_dict()

        # Filter the data for entries with "0 days"
        zero_days_data = data[data['Days to no Cooking'] == 0]

        # Count the number of entries for each "M/TSR Name" with "0 days"
        zero_days_counts = zero_days_data['M/TSR Name'].value_counts().to_dict()

        # Ensure all names are included with a default count of 0
        zero_days_counts = {name: zero_days_counts.get(name, 0) for name in all_mtsr_names}

        # Filter and count for "0-3 days"
        zero_to_three_days_data = data[data['Days to no Cooking'] <= 3]
        zero_to_three_days_counts = zero_to_three_days_data['M/TSR Name'].value_counts().to_dict()

        # Filter and count for "0-5 days"
        zero_to_five_days_data = data[data['Days to no Cooking'] <= 5]
        zero_to_five_days_counts = zero_to_five_days_data['M/TSR Name'].value_counts().to_dict()

        # Filter and count for "0-7 days"
        zero_to_seven_days_data = data[data['Days to no Cooking'] <= 7]
        zero_to_seven_days_counts = zero_to_seven_days_data['M/TSR Name'].value_counts().to_dict()

        current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        return render_template('index.html', 
                               zero_days_counts=zero_days_counts,
                               zero_to_five_days_counts=zero_to_five_days_counts,
                               zero_to_three_days_counts=zero_to_three_days_counts,
                               zero_to_seven_days_counts=zero_to_seven_days_counts,
                               current_time=current_time,
                               customer_info=customer_info)
    else:
        current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        return render_template('index.html', zero_days_counts={}, zero_to_five_days_counts={}, zero_to_three_days_counts={}, zero_to_seven_days_counts={}, current_time=current_time, customer_info={})

@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_file_path
    if 'file' not in request.files:
        return jsonify(success=False)

    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False)

    if file and file.filename.endswith('.xlsx'):
        # Define the directory where files will be uploaded
        upload_directory = '/Users/lameck/Desktop/work_automation/uploads'
        
        # Create the directory if it doesn't exist
        os.makedirs(upload_directory, exist_ok=True)
        
        # Construct the full file path
        file_path = os.path.join(upload_directory, file.filename)
        
        # Save the file
        file.save(file_path)
        uploaded_file_path = file_path
        return jsonify(success=True)

    return jsonify(success=False)

if __name__ == '__main__':
    app.run(debug=True)
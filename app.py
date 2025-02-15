import pandas as pd  
from flask import Flask, render_template, request, jsonify, send_file
import io
import os

app = Flask(__name__)

# Define a global variable to store the uploaded file path
uploaded_file_path = None

@app.route('/')
def show_days_counts():
    if uploaded_file_path:
        try:
            # Attempt to read from sheet 1
            data = pd.read_excel(uploaded_file_path, sheet_name=1)
        except Exception as e:
            print(f"Error reading sheet 1: {e}. Falling back to sheet 0.")
            # If there's an error, fall back to sheet 0
            data = pd.read_excel(uploaded_file_path, sheet_name=0)

        # Get all unique M/TSR Names
        all_mtsr_names = data['M/TSR Name'].unique()

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

        return render_template('index.html', 
                               zero_days_counts=zero_days_counts,
                               zero_to_five_days_counts=zero_to_five_days_counts,
                               zero_to_three_days_counts=zero_to_three_days_counts,
                               zero_to_seven_days_counts=zero_to_seven_days_counts)
    else:
        return render_template('index.html', zero_days_counts={}, zero_to_five_days_counts={}, zero_to_three_days_counts={}, zero_to_seven_days_counts={})

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

@app.route('/export_csv')
def export_to_csv():
    if uploaded_file_path:
        data = pd.read_excel(uploaded_file_path, sheet_name=1)
        # Get all unique M/TSR Names
        all_mtsr_names = data['M/TSR Name'].unique()

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

        # Create a DataFrame from the counts
        df = pd.DataFrame({
            'M/TSR Name': zero_days_counts.keys(),
            '0 Days': zero_days_counts.values(),
            '0-3 Days': [zero_to_three_days_counts.get(name, 0) for name in zero_days_counts.keys()],
            '0-5 Days': [zero_to_five_days_counts.get(name, 0) for name in zero_days_counts.keys()],
            '0-7 Days': [zero_to_seven_days_counts.get(name, 0) for name in zero_days_counts.keys()]
        })

        # Create a CSV file in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='mtsr_counts.csv', mimetype='text/csv')

    return jsonify(success=False)

if __name__ == '__main__':
    app.run(debug=True)
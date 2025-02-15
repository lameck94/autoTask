import pandas as pd
from flask import Flask, request, render_template, jsonify, send_file
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to process the uploaded Excel file
def process_file(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        sheet_name = "Sheet1" if "Sheet1" in xls.sheet_names else xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        if df.shape[0] < 4 or df.shape[1] < 21:
            return "Invalid file format. Please select a valid data file.", None
        
        df_clean = df.iloc[3:, [13, 17, 18, 19, 20]].dropna()
        df_clean.columns = ["M/TSR Name", "0 Days Customers", "0-3 Days Customers", "0-5 Days Customers", "0-7 Days Customers"]
        
        for col in ["0 Days Customers", "0-3 Days Customers", "0-5 Days Customers", "0-7 Days Customers"]:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        
        df_grouped = df_clean.groupby("M/TSR Name").sum().reset_index()
        return None, df_grouped
    except Exception as e:
        return f"Failed to process file: {e}", None

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file uploaded."
        else:
            file = request.files['file']
            if file.filename == '':
                error = "No file selected."
            elif file and file.filename.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                error, data = process_file(file_path)
            else:
                error = "Invalid file type. Please upload an Excel file."
    
    return render_template('index.html', data=data, error=error)

@app.route('/download_csv')
def download_csv():
    if not os.listdir(UPLOAD_FOLDER):
        return "No processed file available."
    
    file_path = os.path.join(UPLOAD_FOLDER, os.listdir(UPLOAD_FOLDER)[1])
    error, df_grouped = process_file(file_path)
    
    if df_grouped is None:
        return jsonify({"error": error})
    
    output = io.StringIO()
    df_grouped.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='processed_data.csv', mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)

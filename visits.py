from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import os
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

UPLOAD_FOLDER = '/Users/lameck/Desktop/work_automation/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith(('.xlsx', '.xls')):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            # Read the Excel file using pandas
            df = pd.read_excel(file_path)
            # Fill any NaN values with 0
            df = df.fillna(0)
            # Remove duplicates but keep the first occurrence
            df = df.drop_duplicates(keep='first')
            # Remove rows where "Total Visits" is 0
            df = df[df['Total Visits'] != 0]
            # Check if required columns exist
            if {"Total Visits", "X TSR Name", "customer_id"}.issubset(df.columns):
                # Group by "M/TSR Name" and count "Total Visits"
                result_df = df.groupby('X TSR Name')['Total Visits'].count().reset_index()
                # Get the count of displayed rows
                row_count = len(result_df)
                # Calculate the average of "Total Visits"
                average_visits = result_df['Total Visits'].mean()
                # Create a DataFrame for the average row
                average_row = pd.DataFrame([{'X TSR Name': 'Average', 'Total Visits': average_visits}])
                # Concatenate the average row to the result DataFrame
                result_df = pd.concat([result_df, average_row], ignore_index=True)
                # Format "Total Visits" to remove decimal points
                result_df['Total Visits'] = result_df['Total Visits'].astype(int)
                # Display the result DataFrame and row count
                return f'''
                <!doctype html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Upload Excel File</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background-color: #f4f7f9;
                            margin: 20px;
                        }}
                        h1 {{
                            color: #333;
                            text-align: center;
                            margin-bottom: 30px;
                        }}
                        form {{
                            text-align: center;
                            margin-bottom: 20px;
                        }}
                        button {{
                            padding: 10px 20px;
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            cursor: pointer;
                            border-radius: 5px;
                            transition: background-color 0.3s ease;
                        }}
                        button:hover {{
                            background-color: #45a049;
                        }}
                        table {{
                            width: 100%;
                            max-width: 100%;
                            margin: 20px auto;
                            border-collapse: collapse;
                            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            border-radius: 5px;
                            overflow: hidden;
                        }}
                        th, td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: center;
                            font-size: 0.9em;
                        }}
                        th {{
                            background-color: #4CAF50;
                            color: white;
                        }}
                        tr:nth-child(even) {{
                            background-color: #f9f9f9;
                        }}
                        tr:hover {{
                            background-color: #e0e0e0;
                        }}
                        .error {{
                            color: red;
                            text-align: center;
                        }}
                    </style>
                </head>
                <body>
                    <p>Staff present: {row_count}</p>
                    {result_df.to_html(index=False)}
                    <!-- Removed export form -->
                </body>
                </html>
                '''
            else:
                missing_columns = {"Total Visits", "M/TSR Name", "customer_id"} - set(df.columns)
                return f'''
                <!doctype html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Visits File</title>
                    <style>
                        /* Include the same styles as above */
                    </style>
                </head>
                <body>
                    <h1>Visits File</h1>
                    <form id="uploadForm" method=post enctype=multipart/form-data>
                      <input type=file name=file id="fileInput" style="display:none;" onchange="document.getElementById('uploadForm').submit();">
                      <button type="button" onclick="document.getElementById('fileInput').click();">Choose File</button>
                    </form>
                    <h2 class="error">Error: The file is missing the following required columns: {', '.join(missing_columns)}</h2>
                    <p>Please ensure your Excel file includes these columns and try again.</p>
                </body>
                </html>
                '''
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visits</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f9;
                margin: 20px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            form {
                text-align: center;
                margin-bottom: 20px;
            }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Visits</h1>
        <form id="uploadForm" method=post enctype=multipart/form-data>
          <input type=file name=file id="fileInput" style="display:none;" onchange="document.getElementById('uploadForm').submit();">
          <button type="button" onclick="document.getElementById('fileInput').click();">Choose File</button>
        </form>
    </body>
    </html>
    '''

# Removed the /export_csv route

if __name__ == '__main__':
    app.run(debug=True)
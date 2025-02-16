from flask import Flask, request, render_template, redirect, url_for, session, send_file
import pandas as pd
import os
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration
UPLOAD_FOLDER = '/Users/lameck/Desktop/work_automation/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_excel_data(df):
    """Process the Excel data and return the result DataFrame"""
    df = df.fillna(0)
    df = df.drop_duplicates(keep='first')
    df = df[df['Total Visits'] != 0]
    return df

def create_result_table(df):
    """Create and format the result table"""
    result_df = df.groupby('X TSR Name')['Total Visits'].count().reset_index()
    result_df = result_df.sort_values('Total Visits', ascending=False)
    
    # Calculate and add average row
    average_visits = result_df['Total Visits'].mean()
    average_row = pd.DataFrame([{'X TSR Name': 'Average', 'Total Visits': average_visits}])
    result_df = pd.concat([result_df, average_row], ignore_index=True)
    
    # Format numbers
    result_df['Total Visits'] = result_df['Total Visits'].astype(int)
    return result_df

def format_html_table(result_df):
    """Format the DataFrame as HTML with styling"""
    html_table = result_df.to_html(index=False, classes='dataframe')
    return html_table

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '' or not file.filename.endswith(('.xlsx', '.xls')):
            return redirect(request.url)

        # Save and process file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        df = pd.read_excel(file_path)

        # Check required columns
        required_columns = {"Total Visits", "X TSR Name", "customer_id"}
        if not required_columns.issubset(df.columns):
            missing_columns = required_columns - set(df.columns)
            return render_template('template.html', 
                                row_count=0, 
                                html_table=f'<p class="error">Missing columns: {", ".join(missing_columns)}</p>')

        # Process data and create table
        df = process_excel_data(df)
        result_df = create_result_table(df)
        html_table = format_html_table(result_df)

        # Store for export and render
        session['export_data'] = result_df.to_csv(index=False)
        return render_template('template.html', 
                            row_count=len(result_df) - 1, 
                            html_table=html_table, 
                            show_export=True)

    return render_template('template.html', row_count=0, html_table='', show_export=False)

@app.route('/export', methods=['GET'])
def export():
    if 'export_data' in session:
        output = io.BytesIO()
        output.write(session['export_data'].encode())
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='visits_report.csv'
        )
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
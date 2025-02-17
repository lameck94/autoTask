from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
            df = pd.read_excel(file_path)
            html_table = df.to_html(classes='table table-striped', index=False)
            return render_template('inaind.html', table=html_table)  # Using inaind.html
    return render_template('inaind.html', table=None)  # Using inaind.html

if __name__ == '__main__':
    app.run(debug=True)
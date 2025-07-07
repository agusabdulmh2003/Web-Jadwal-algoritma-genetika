from flask import Flask, render_template, request, redirect, send_from_directory
import pandas as pd
import os
from genetic_scheduler import run_scheduler

os.makedirs('static', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = {}
        for name in ['classes', 'subjects', 'teachers', 'timeslots']:
            uploaded = request.files[name]
            filepath = os.path.join(UPLOAD_FOLDER, uploaded.filename)
            uploaded.save(filepath)
            files[name] = pd.read_csv(filepath)

        schedule_df, chart_path = run_scheduler(files)
        schedule_df.to_csv(os.path.join(STATIC_FOLDER, 'schedule.csv'), index=False)

        return render_template('index.html', schedule=schedule_df.to_html(index=False), chart_path='chart.png')

    return render_template('index.html')

@app.route('/download')
def download_file():
    return send_from_directory(STATIC_FOLDER, 'schedule.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
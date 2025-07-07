from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import os
from genetic_scheduler import run_scheduler

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    schedule = None
    chart_path = None
    classes_list = []  # Daftar kelas untuk filter

    if request.method == 'POST':
        files = {}
        required_files = ['classes', 'subjects', 'teachers', 'timeslots']
        
        for name in required_files:
            uploaded = request.files[name]
            if uploaded.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded.filename)
                uploaded.save(filepath)
                files[name] = pd.read_csv(filepath)
        
        if len(files) == 4:
            try:
                schedule_df, chart_path = run_scheduler(files)
                schedule = schedule_df.to_dict('records')
                
                # Ekstrak daftar kelas unik untuk filter
                classes_list = sorted(schedule_df['Kelas'].unique().tolist())
            except Exception as e:
                print(f"Error generating schedule: {str(e)}")
    
    return render_template('index.html', 
                          schedule=schedule, 
                          chart_path=chart_path,
                          classes_list=classes_list)

@app.route('/download')
def download_file():
    return send_from_directory(STATIC_FOLDER, 'schedule.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
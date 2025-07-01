from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import resume_extract
import job_role_prediction
import linkdin_jobs

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process_resume():
    if 'resume' not in request.files:
        return 'No file part', 400
    file = request.files['resume']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract resume info
        text = resume_extract.extract_text_from_pdf(filepath)
        info = resume_extract.extract_resume_info(text)

        # Get model predicted job role
        job_role = job_role_prediction.predict_job_role(info['Skills'],info['Experience'], info['Qualification'])

        # For demo, use 'India' as location
        location = request.form.get('location')

        # Search jobs using linkdin_jobs
        jobs_df = linkdin_jobs.linkdin(job_role, location, info['Skills'], info['Qualification'])
        jobs = []
        for _, row in jobs_df.iterrows():
            jobs.append({
                'title': row.get('Job Title', ''),
                'company': row.get('Company Name', ''),
                'location': row.get('Location', ''),
                'description': ', '.join(row.get('Skills', [])),
                'link': row.get('Apply Link', '#')
            })
        return render_template('recommendations.html',
                               name=info['Name'],
                               job_role=job_role,
                               skills=info['Skills'],
                               qualification=info['Qualification'],
                               experience=info['Experience'],
                               jobs=jobs)
    else:
        return 'Invalid file type. Only PDF allowed.', 400

if __name__ == '__main__':
    app.run()

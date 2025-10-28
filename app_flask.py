from flask import Flask, render_template, request, jsonify, session
import os
from werkzeug.utils import secure_filename
from resume_parser import ResumeParser
from ats_analyzer import ATSAnalyzer
from cover_letter_generator import CoverLetterGenerator
from job_api import JobAPI
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
parser = ResumeParser()
analyzer = ATSAnalyzer()
cover_generator = CoverLetterGenerator()
job_api = JobAPI()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Parse resume
        resume_text = parser.extract_text(file)
        session['resume_text'] = resume_text
        
        # Analyze with ATS
        ats_score, feedback = analyzer.analyze_resume(resume_text)
        
        return jsonify({
            'success': True,
            'ats_score': ats_score,
            'feedback': feedback,
            'resume_length': len(resume_text)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/match_job', methods=['POST'])
def match_job():
    data = request.get_json()
    job_description = data.get('job_description', '')
    
    if not session.get('resume_text'):
        return jsonify({'error': 'No resume uploaded'}), 400
    
    try:
        resume_text = session['resume_text']
        analysis = analyzer.match_job_description(resume_text, job_description)
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/enhance_resume', methods=['POST'])
def enhance_resume():
    data = request.get_json()
    target_score = data.get('target_score', 90)
    
    if not session.get('resume_text'):
        return jsonify({'error': 'No resume uploaded'}), 400
    
    try:
        resume_text = session['resume_text']
        enhanced_resume = analyzer.generate_enhanced_resume(resume_text, target_score)
        return jsonify({'enhanced_resume': enhanced_resume})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():
    data = request.get_json()
    company_name = data.get('company_name', '')
    position = data.get('position', '')
    job_description = data.get('job_description', '')
    tone = data.get('tone', 'professional')
    
    if not session.get('resume_text'):
        return jsonify({'error': 'No resume uploaded'}), 400
    
    if not all([company_name, position, job_description]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        resume_text = session['resume_text']
        cover_letter = cover_generator.generate_cover_letter(
            resume_text, job_description, company_name, position, tone
        )
        return jsonify({'cover_letter': cover_letter})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    data = request.get_json()
    job_title = data.get('job_title', '')
    location = data.get('location', '')
    experience_level = data.get('experience_level', '')
    
    if not job_title:
        return jsonify({'error': 'Job title is required'}), 400
    
    try:
        jobs = job_api.search_jobs(job_title, location, experience_level)
        return jsonify({'jobs': jobs})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5000)
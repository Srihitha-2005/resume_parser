from flask import Flask, request, render_template, redirect, url_for, session, flash
import os
from resume_parser import parse_resume
from bert import calculate_similarity
from db import init_db, create_user, authenticate_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if authenticate_user(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('upload'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords don't match")
        else:
            success = create_user(request.form['username'], request.form['password'], request.form['full_name'])
            if success:
                return redirect(url_for('login'))
            else:
                flash("Username already exists")
    return render_template('signup.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Check if files were uploaded
        if 'resumes' not in request.files:
            flash("No files uploaded")
            return redirect(request.url)
        
        # Check if job description exists
        job_desc = request.form.get('job_description')
        if not job_desc or not job_desc.strip():
            flash("Job description is required")
            return redirect(request.url)
        
        files = request.files.getlist('resumes')
        results = []
        best_match = None
        highest_score = -1

        for file in files:
            if file.filename == '':
                continue
            
            if file:
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)

                try:
                    parsed = parse_resume(path)
                    resume_text = " ".join(str(v) for v in parsed.values() if v)
                    score = calculate_similarity(resume_text, job_desc)
                    
                    result = {
                        "filename": filename,
                        "name": parsed.get("name", "N/A"),
                        "email": ", ".join(parsed.get("email", ["N/A"])),
                        "phone": ", ".join(parsed.get("phone", ["N/A"])),
                        "score": round(score, 4)
                    }
                    results.append(result)
                    
                    # Track best match
                    if score > highest_score:
                        highest_score = score
                        best_match = result
                        
                except Exception as e:
                    flash(f"Error processing {filename}: {str(e)}")
                finally:
                    # Clean up the file
                    if os.path.exists(path):
                        os.remove(path)
        
        # Sort results by score (highest first)
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return render_template('upload.html', results=results, best_match=best_match)
    
    return render_template('upload.html', results=None, best_match=None)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

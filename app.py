from flask import Flask, request, redirect, render_template, url_for, send_from_directory
import os
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
f = request.files['zipfile']
if not f:
return 'No file', 400
fname = str(uuid.uuid4()) + '.zip'
path = os.path.join(UPLOAD_FOLDER, fname)
f.save(path)
# Run checker
outdir = os.path.join('checker_runs', fname)
os.makedirs(outdir, exist_ok=True)
subprocess.Popen(['python3', '../checker/checker.py', path, '--out', outdir])
return redirect(url_for('results', run_id=fname))
@app.route('/results/<run_id>')
def results(run_id):
outdir = os.path.join('checker_runs', run_id)
json_path = os.path.join(outdir, 'report.json')
txt_path = os.path.join(outdir, 'report.txt')
return render_template('results.html', json_path=json_path, txt_path=txt_path)

if __name__ == '__main__':
app.run(debug=True)

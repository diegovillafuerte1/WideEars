import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
UPLOAD_FOLDER = 'known_faces/'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        reciever_id = request.form["recieverId"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{reciever_id}.jpg"))
            return redirect(url_for('uploaded_file',
                                    filename=f"{receiver_id}.jpg"))
    return '''
    <!doctype html>
    <title>New User Registration</title>
    <h1>Upload JPG of face and enter corresponding receiver ID into textbox</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file> 
      <input type=text name=recieverId>
      
      <input type=submit value=Upload>
    </form>
    '''





@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

app.run(host="0.0.0.0")
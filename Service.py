from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session
from flask.helpers import flash
from flask.templating import render_template
from wtforms import Form, StringField, PasswordField, BooleanField
from functools import wraps
from configparser import ConfigParser
from lib import Analyze
from lib import CoursePrerequisites
import os


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function


config = ConfigParser()
app = Flask(__name__)
config.read("./config.ini")
app.config['SECRET_KEY'] = os.urandom(12)
app.config["ROOT_PATH"] = os.path.join(os.path.dirname(__file__))

#region SERVE SVELTE APP
static_path = os.path.join(app.config["ROOT_PATH"], "frontend", "public")
templates_path = os.path.join(static_path, 'templates')
app.template_folder = templates_path

@app.route('/')
def index():
    print(static_path, "index.html")
    return send_from_directory(static_path, "index.html")

@app.route('/<path:path>')
def statics(path):
    return send_from_directory(static_path, path)
#endregion


app.config["CATALOG_PATH"] = os.path.join(app.config["ROOT_PATH"], 'Catalogs')

@app.route('/terms')
def getTerms():
    return jsonify([file[:file.find('.')] for file in os.listdir(app.config["CATALOG_PATH"]+'/Originals') if os.path.isfile(os.path.join(app.config["CATALOG_PATH"]+'/Originals', file))])


@app.route('/prerequisites')
def getPrerequisites():
    term = request.args.get('term')
    path = os.path.join(app.config['CATALOG_PATH'], 'Originals')
    return send_from_directory(path, term + '.json')


@app.route('/changes')
def getChanges():
    term = request.args.get('term')
    path = os.path.join(app.config['CATALOG_PATH'], 'Changes')
    return send_from_directory(path, term + '.json')


@app.route('/updates')
def getUpdates():
    term = request.args.get('term')
    path = os.path.join(app.config['CATALOG_PATH'], 'Updates')
    return send_from_directory(path, term + '.json')


@app.route('/upload', methods=["GET", "POST"])
@login_required
def uploadCatalog():
    
    if request.method == 'GET':
        return send_from_directory(templates_path, "upload.html")


    if "file" not in request.files:
        return jsonify({"message": "Please attach a file.", "isSuccess": False})


    catalog = request.files['file']
    term = request.args.get('term')

    if os.path.isfile(app.config['CATALOG_PATH']+'/Originals/' + term + '.json'):
        return(jsonify({
            "message": "Course catalog has already been uploaded to the system and analyzed.",
            "isSuccess": False
        }))

    CoursePrerequisites(catalog, term)
    try:
        Analyze(term)
        return(jsonify({
            "message": "Course catalog was uploaded to the system and analyzed.",
            "isSuccess": True
        }))
    except Analyze.CycleError as e:
        # delete the faulty catalog from storage
        os.remove(app.config['CATALOG_PATH']+'/Originals/' + term + '.json')

        return jsonify({
            "message": "Course catalog has cycles, analysis was not completed.",
            "errors": e.cyclics,
            "isSuccess": False
        })


@app.route('/delete', methods=["GET", "POST"])
@login_required
def deleteCatalog():
    
    if request.method == 'GET':
        return send_from_directory(templates_path, "delete.html")
    
    
    term = request.args.get('term')

    if os.path.isfile(app.config['CATALOG_PATH'] + '/Originals/' + term + '.json'):
        os.remove(app.config['CATALOG_PATH'] + '/Originals/' + term + '.json')
    
    if os.path.isfile(app.config['CATALOG_PATH'] + '/Changes/' + term + '.json'):
        os.remove(app.config['CATALOG_PATH'] + '/Changes/' + term + '.json')

    if os.path.isfile(app.config['CATALOG_PATH'] + '/Updates/' + term + '.json'):
        os.remove(app.config['CATALOG_PATH'] + '/Updates/' + term + '.json')

    return(jsonify({
        "message": "Course catalog and analyzes have been successfully deleted from the system.",
        "isSuccess": True
    }))


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        if username == config['Admin']['username'] and password == config['Admin']['password']:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Username or password is wrong', 'danger')
            return redirect(url_for('login'))
     
    return send_from_directory(templates_path, "login.html")    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    return send_from_directory(templates_path, "admin.html")


if __name__ == "__main__":
    app.run(
        host=config["Service"]["host"],
        port=int(config["Service"]["port"]),
        debug=True
    )

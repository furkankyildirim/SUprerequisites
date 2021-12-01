from flask import Flask, request, jsonify, send_file
from configparser import ConfigParser
from .analysis import Analyze
from .script import CoursePrerequisites
import os

config = ConfigParser()
config.read("./config.ini")
app = Flask(__name__)

app.config["CATALOG_PATH"] = os.path.join(os.path.dirname(__file__), '..', 'Catalogs')

@app.route('/')
def index():
    data = dict()
    data['name'] = 'Sabancı University Analyzing Course Prerequisites'
    return jsonify(data)


@app.route('/upload')
def uploadCatalog():
    catalog = request.files['file']
    term = request.args.get('term')
    #CoursePrerequisites(catalog,term)
    Analyze(term)
    return(jsonify({"message":"successful"}))


@app.route('/prerequisites')
def getPrerequisites():
    term = request.args.get('term')
    return send_file(app.config['CATALOG_PATH']+'/Originals/' + term + '.json')


@app.route('/changes')
def getChanges():
    term = request.args.get('term')
    return send_file(app.config['CATALOG_PATH']+'/Changes/' + term + '.json')


@app.route('/updates')
def getUpdates():
    term = request.args.get('term')
    return send_file(app.config['CATALOG_PATH']+'/Updates/' + term + '.json')


if __name__ == "__main__":
    app.run(
        host=config["Service"]["host"],
        port=int(config["Service"]["port"]),
        debug=True
    )
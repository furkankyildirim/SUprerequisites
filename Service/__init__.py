from flask import Flask, request, jsonify, send_file
from configparser import ConfigParser
from .analysis import Analyze
from .script import CoursePrerequisites
import os

config = ConfigParser()
config.read("./config.ini")
app = Flask(__name__)

app.config["CATALOG_PATH"] = os.path.join(
    os.path.dirname(__file__), '..', 'Catalogs')


@app.route('/')
def index():
    data = dict()
    data['name'] = 'Sabancı University Analyzing Course Prerequisites'
    return jsonify(data)


@app.route('/upload')
def uploadCatalog():

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
        return jsonify({
            "message": "Course catalog has cycles, analysis was not completed.",
            "errors": e.cyclics,
            "isSuccess": False
        })



@app.route('/delete')
def deleteCatalog():
    term = request.args.get('term')

    if os.path.isfile(app.config['CATALOG_PATH'] + '/Originals/' + term + '.json'):
        os.remove(app.config['CATALOG_PATH'] + '/Originals/' + term + '.json')
        os.remove(app.config['CATALOG_PATH'] + '/Changes/' + term + '.json')
        os.remove(app.config['CATALOG_PATH'] + '/Updates/' + term + '.json')

        return(jsonify({
            "message": "Course catalog and analyzes have been successfully deleted from the system.",
            "isSuccess": True
        }))

    else:
        return(jsonify({
            "message": "Course catalog and analysis are not available in the system.",
            "isSuccess": False
        }))


@app.route('/prerequisites')
def getPrerequisites():
    term = request.args.get('term')
    return send_file(app.config['CATALOG_PATH'] + '/Originals/' + term + '.json')


@app.route('/changes')
def getChanges():
    term = request.args.get('term')
    return send_file(app.config['CATALOG_PATH'] + '/Changes/' + term + '.json')


@app.route('/updates')
def getUpdates():
    term = request.args.get('term')
    return send_file(app.config['CATALOG_PATH'] + '/Updates/' + term + '.json')


if __name__ == "__main__":
    app.run(
        host=config["Service"]["host"],
        port=int(config["Service"]["port"]),
        debug=True
    )

from flask import Flask, request, jsonify, send_file, send_from_directory
from configparser import ConfigParser
from lib import Analyze
from lib import CoursePrerequisites
import os

config = ConfigParser()
config.read("./config.ini")
app = Flask(__name__)

app.config["ROOT_PATH"] = os.path.join(os.path.dirname(__file__))

#region SERVE SVELTE APP
static_path = os.path.join(app.config["ROOT_PATH"], "frontend", "public")
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
        # delete the faulty catalog from storage
        os.remove(app.config['CATALOG_PATH']+'/Originals/' + term + '.json')

        return jsonify({
            "message": "Course catalog has cycles, analysis was not completed.",
            "errors": e.cyclics,
            "isSuccess": False
        })

# this should be behind authorization checks
"""
@app.route('/delete', methods=["DELETE"])
def deleteCatalog():
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
"""


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

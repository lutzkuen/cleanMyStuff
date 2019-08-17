#!flask/bin/python
"""
Author: Lutz Künneke

The server will accept connections from different types of clients. Overall we want to build a database showing names and MD5 of files on different devices to identify duplicates
"""

from flask import Flask, jsonify, abort, make_response, request
import dataset
import code
import datetime

app = Flask(__name__)


# DB_PATH = 'sqlite:///files.db'
DB_PATH = 'postgresql+psycopg2:///cleaner'
KF_TABNAME = 'knownfiles'
DB = dataset.connect(DB_PATH)
F_TABLE = DB[KF_TABNAME]

@app.route('/')
def index():
    return 'Server is running'

@app.route('/v1/files', methods=['GET'])
def get_files():
    rows = jsonify({'files': [row for row in F_TABLE.all()]})
    return rows

@app.route('/v1/file', methods=['POST'])
def get_file():
    if (not request.json) or (not request.content_type == 'application/json'):
        abort(400)
    result_lines = {'files': [row for row in F_TABLE.find(full_path=request.json['full_path'])]}
    rows = jsonify(result_lines)
    return rows

@app.route('/v1/remove_file', methods=['POST'])
def remove_file():
    if (not request.json) or (not request.content_type == 'application/json'):
        abort(400)
    res = F_TABLE.delete(full_path=request.json['full_path'])
    return jsonify({'removed': res})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/v1/add_file', methods=['POST'])
def create_file():
    if (not request.json) or (not request.content_type == 'application/json'):
        abort(400)
    new_file = {
        'full_path': request.json['full_path'],
        'record_source': request.json['record_source'],
        'content_md5': request.json['content_md5'],
        'last_seen': datetime.datetime.now()
    }
    F_TABLE.upsert(new_file, ['full_path', 'record_source'])
    return jsonify({'file': new_file}), 201


if __name__ == '__main__':
    app.run(debug=True)

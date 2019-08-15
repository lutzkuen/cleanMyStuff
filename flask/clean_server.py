#!flask/bin/python
"""
Author: Lutz Künneke

The server will accept connections from different types
"""

from flask import Flask, jsonify, abort, make_response, request
import dataset
import code

app = Flask(__name__)


DB_PATH = 'sqlite:///files.db'

@app.route('/')
def index():
    return 'test'

@app.route('/v1/files', methods=['GET'])
def get_files():
    db = dataset.connect(DB_PATH)
    f_table = db['files']
    return jsonify({'files': [row for row in f_table.all()]})

@app.route('/v1/files/<string:file_path>', methods=['GET'])
def get_file(file_path):
    db = dataset.connect(DB_PATH)
    f_table = db['files']
    return jsonify({'files': [row for row in f_table.find(path=file_path)]})

@app.route('/v1/remove_file/<string:file_path>', methods=['GET'])
def remove_file(file_path):
    db = dataset.connect(DB_PATH)
    f_table = db['files']
    res = f_table.delete(path=file_path)
    return jsonify({'removed': res})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/v1/files', methods=['POST'])
def create_file():
    print(request.content_type)
    if (not request.json) or (not request.content_type == 'application/json'):
        abort(400)
    new_file = {
        'path': request.json['path'],
        'content': request.json['content'],
        'device': request.json['device']
    }
    db = dataset.connect(DB_PATH)
    f_table = db['files']
    f_table.upsert(new_file, ['path'])
    return jsonify({'file': new_file}), 201


if __name__ == '__main__':
    app.run(debug=True)
#! python3
# Flask webservice app to fetch queries via API

import sys
from flask import Flask, jsonify, request
from get_jobs import get_jobs

app = Flask(__name__)

@app.route('/SAP/api/v1.0/jobs/<string:string>', methods=['GET'])
def fetch(string):
    return jsonify(get_jobs(string))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

# Main entry point for script
def main():
    app.run(debug=True)

if __name__ == '__main__':
    sys.exit(main())
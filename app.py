import re
from datetime import datetime
from git import Repo
import os
import subprocess
import json

from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = os.urandom(16)


@app.route("/")
def home():
    return render_template("index.html")


def lint_file(filePath):
    result = ''
    try:
        result = subprocess.check_output(
            ['flake8', '--format=json', filePath])
    except subprocess.CalledProcessError as e:
        result = e.output
    return result


def byteString_to_json(byteString):
    string = byteString.decode("utf-8")
    dictionary = eval(string)
    jsonFormattedString = json.dumps(dictionary)
    return json.loads(jsonFormattedString)


def lintIt(git_url, relativeFilePath):
    destination = os.path.join('.', 'repo')
    Repo.clone_from(git_url, destination)
    filePath = os.path.join(destination, relativeFilePath)

    resultString = lint_file(filePath)

    # Delete cloned directory
    os.system('rmdir /S /Q "{}"'.format(destination))

    # Convert byte string to JSON
    result = byteString_to_json(resultString)
    session['result'] = result
    return redirect(url_for('success'))


@app.route("/lint", methods=['POST', 'GET'])
def lint():
    if request.method == 'POST':
        if request.data:
            # If incoming request data is sent as string
            git_url = request.get_json().get('repoUrl')
            relativeFilePath = request.get_json().get('filePath')
        elif request.form:
            # If incoming request data is sent as HTTP post form
            git_url = request.form.get('repoUrl')
            relativeFilePath = request.form.get('filePath')

        return lintIt(git_url, relativeFilePath)

    return render_template("lint.html")


@app.route('/success')
def success():
    if 'result' in session:
        print(session['result'])
        return render_template("success.html", result=session['result'])
    return ''

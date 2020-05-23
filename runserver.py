# -*- coding: utf-8 -*-
"""
This script runs the Flask application using a development server.
"""

from os import environ
from Flask import app

if __name__ == '__main__':
    #app.run(host="192.168.8.103", port=80, debug=True)
    app.run(host="192.168.43.151", port=80, debug=True)


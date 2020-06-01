# -*- coding: utf-8 -*-
"""
This script runs the Flask application using a development server.
"""

from os import environ
from Flask import app
import config
if __name__ == '__main__':
    #app.run(host="192.168.8.128", port=80, debug=config.DEBUG)
    app.run(host="192.168.43.151", port=80, debug=config.DEBUG)


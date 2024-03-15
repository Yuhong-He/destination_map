import logging
import logging.handlers
import os

from flask import jsonify


def make_response(code, msg, data=None):
    response = {
        "code": code,
        "msg": msg,
        "data": data
    }
    return jsonify(response)

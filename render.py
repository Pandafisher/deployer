# coding: utf-8
from flask import Response, json


def dump(data, status_code=200):
    return Response(json.dumps(data),
                    mimetype='application/json', status=status_code)


def ok(content=''):
    msg = {
        'status': 'ok',
        'content': content,
    }

    resp = dump(msg)
    return resp


def error(error='', status_code=400):
    if isinstance(error, (tuple, list)):
        msg = {
            'status': 'error',
            'code': error[0],
            'msg': error[1],
        }
    else:
        msg = {
            'status': 'error',
            'msg': error,
        }

    resp = dump(msg, status_code=status_code)
    return resp

from flask import jsonify
from app import db


def dbadd(object):
    db.session.add(object)
    db.session.commit()

    return True


def dbdel(model, **kwargs):
    for value in kwargs.values():
        if not value:
            return None

    db.session.query(model).filter_by(**kwargs).delete()
    return True


def json_message(status=200, msgkey='message',msg = None):
    if msgkey == 'message':
        message = {'status': status, 'message': msg}
    elif msgkey == 'error':
        message = {'status': status, 'error': msg}
    return jsonify(message)

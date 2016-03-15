from flask import request, jsonify, abort, g, make_response, session ,abort

from functools import wraps

from app import app

from .models import User, Token
from .api import dbadd, dbdel, json_message

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Uri Not Found or Error'}))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        userid = session.get('userid', None)
        tokenid = session.get('tokenid', None)
        if userid is None or tokenid is None:
            return jsonify({'status': 401, 'error': 'Authentication False'})
        try:
            olduserid = Token.query.filter_by(token=tokenid).first().userid
        except:
            return jsonify({'status': 401, 'error': 'Authentication False'})
        if userid != olduserid:
            return jsonify({'status': 401, 'error': 'Authentication False'})
        return f(*args, **kwargs)
    return decorated_function


@app.route('/test/<int:id>')
@login_required
def hello(id):
    tt = [
    {
        'id':1,
        'titie':'haha'
    },
    {
        'id':2,
        'titile':'sdfsdf'
    }]
    task = filter(lambda t: t['id'] == id, tt)
    if len(task) == 0:
        abort(404)

    return jsonify({'task':task[0]})


@app.route('/oauth/user/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'status': 530, 'error': 'username or password is None '})

    userobj = User.query.filter_by(username = username).first()

    if not userobj:
        return json_message(200, 'error', 'User is not exist')

    if not userobj.verify_password(password):
        return json_message(200, 'error', 'Password Error')

    userid = userobj.id

    #Generate user token
    token = userobj.generate_auth_token(600)

    #Write user token to DB
    tokenobj = Token(userid = userid, token = token)
    dbadd(tokenobj)

    #Generate session
    session['tokenid'] = token
    session['userid'] = userid
    

    return jsonify({'status': 200, 'message': 'Login Success'})


@app.route('/oauth/user/logout')
@login_required
def logout():
    userid = session.get('userid', None)
    tokenid = session.get('tokenid', None)

    dbdel(Token, userid=userid, token=tokenid)
    session.clear()

    return jsonify({'status': 200, 'message': 'Logout Success'})


from flask import request, jsonify, session
from app import app, db
from views import login_required

from .models import User, Token
from .api import dbadd, dbdel, json_message

from passlib.apps import custom_app_context as pwd_context

@app.route('/oauth/user/add', methods = ['POST'])
def user_add():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'status': 530, 'error': 'username or password is None '})
    if User.query.filter_by(username=username).first() is not None:
    	return json_message(200, 'error', 'user already exists')
        #return jsonify({'status': 200, 'error': 'user already exists'})

    userobj = User(username=username)
    userobj.hash_password(password)
    dbadd(userobj)

    return jsonify({'status': 200, 'message': 'User Register Success'})


@app.route('/oauth/user/changepasswd', methods = ['POST'])
@login_required
def change_passwd():
	userid = session['userid']
	password = request.json.get('password', None)

	if not password:
		return json_message(200, 'error', 'Password is None')

	query = db.session.query(User)
	newpasswd = pwd_context.encrypt(password)

	try:
		query.filter(User.id == userid).update({User.password_hash: newpasswd})
	except Exception:
		return json_message(200, 'error', 'Password Change Failed')

	return json_message(200, 'message', 'Password Change Success')


@app.route('/oauth/user/delete', methods = ['GET'])
@login_required
def user_delete():
	userid = request.args.get('userid', None)
	
	if not userid:
		json_message(200, 'error', 'User Delete Failed')

	dbdel(User, id = userid)

	return json_message(200, 'message', 'User Delete Success')


@app.route('/oauth/user/list', methods=['GET'])
@login_required
def user_list():
    userslist = User.query.all()
    userslist = [{'id': i.id, 'username': i.username} for i in userslist]

    return jsonify({'status': 200, 'userslist': userslist})

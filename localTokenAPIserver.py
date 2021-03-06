"""
Flask based secured API server that serves at http://127.0.0.1:5000
User login:password stored in sql.db
On demand token generated for each user with limited validity
"""

#!/usr/bin/env python
import os
import random
import logging
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

#Setup logging
logging.basicConfig(level=logging.INFO)


# initialization
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    ''' User DB model '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        ''' Encrypt given password'''
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        ''' Verify given password'''
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=None):
        ''' Generate token'''
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        ''' Verify token'''
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    """
    Verify username password against DB value
    Expects username or token with password
    Returns True / False
    """
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    """
    Add new user to sql DB
    Expects Nothing
    Returns jsonified user details
    """
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'username': user.username, 'status': 'already_exists'})
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 202,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    """
    Get user name
    Expects Nothing
    Returns Jsonified user name
    """
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    """
    Generates authorization token for a user
    Expects nothing
    Returns Jsonified token
    """
    token_length = 1200
    token = g.user.generate_auth_token(token_length)
    return jsonify({'token': token.decode('ascii'), 'duration': token_length})


@app.route('/api/test/getCount', methods=['GET'])
@auth.login_required
def get_count():
    """
    simulates API call by returning server_count or error message
    Expects Nothing
    Returns jsonified server_count or error message
    """
    return_response = random.choice([{'count':random.randint(0, 3)},
                                     {'errorCode': 99, 'errorMessage': "API server error"}])
    return jsonify(return_response)

def shutdown_server():
    """
    shutdown server call
    Expects nothing
    Returns nothing
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError(logging.error('Not running with the Werkzeug Server'))
    func()

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """
    shutdown API server
    """
    shutdown_server()
    return logging.info('Server shutting down...')


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
app.run(host= '0.0.0.0', debug=True)

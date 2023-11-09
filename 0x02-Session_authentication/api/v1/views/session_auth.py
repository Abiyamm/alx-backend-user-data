#!/usr/bin/env python3
""" Module of Users views
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User
import os


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def handle_login() -> str:
    """ handles login
    """
    email = request.form.get('email')
    passwd = request.form.get('password')
    user = None

    if not email:
        return jsonify({
            "error": "email missing"
        }), 400
    if not passwd:
        return jsonify({
            "error": "password missing"
        }), 400

    users = User.search({
        'email': email
    })

    if users:
        user = users[0]

    if user is None:
        return jsonify({
            "error": "no user found for this email"
        }), 404
    if user.is_valid_password(passwd) is False:
        return jsonify({
            "error": "wrong password"
        }), 401

    from api.v1.app import auth
    sess_id = auth.create_session(user.id)
    cookie_name = os.getenv('SESSION_NAME')
    resp = jsonify(user.to_json())
    resp.set_cookie(cookie_name, sess_id)
    return resp


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def handle_logout() -> str:
    """ handles logout
    """
    from api.v1.app import auth
    if auth.destroy_session(request):
        return jsonify({})
    abort(404)

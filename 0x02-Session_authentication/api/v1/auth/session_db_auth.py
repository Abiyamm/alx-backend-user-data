#!/usr/bin/env python3
"""
SessionAuth class defined here
"""
from flask import abort, request
from api.v1.auth.session_exp_auth import SessionExpAuth
import uuid
from models.user_session import UserSession
import os
import datetime


class SessionDBAuth(SessionExpAuth):
    """ SessionDBAuth class """

    def create_session(self, user_id=None):
        """ wraps SessionAuth func """
        if user_id is None or type(user_id) != str:
            return
        UserSession.load_from_file()
        user_session = UserSession()
        user_session.user_id = user_id
        sess_id = str(uuid.uuid4())
        user_session.session_id = sess_id
        user_session.save()
        return sess_id

    def user_id_for_session_id(self, session_id=None):
        """ retreives sesion dic from user_id_by_session_id """
        UserSession.load_from_file()
        attr = {
            'session_id': session_id
        }
        user_sessions = UserSession.search(attr)
        user_id = None

        if user_sessions:
            user_session = user_sessions[0]
            user_id = user_session.user_id
        else:
            return None

        if self.session_duration <= 0:
            return user_id

        sess_creation_time = user_session.created_at

        now = datetime.datetime.now()
        live_time = datetime.timedelta(seconds=self.session_duration)

        if now > sess_creation_time + live_time:
            user_session.remove()
            return None

        return user_id

    def destroy_session(self, request=None):
        """ destroys UserSession object """
        if request is None:
            return False
        sess_id = self.session_cookie(request)
        if not sess_id:
            return False
        user_id = self.user_id_for_session_id(sess_id)
        if not user_id:
            return False

        UserSession.load_from_file()
        user_sessions = UserSession.search({
            'session_id': sess_id
        })
        if not user_sessions:
            return False
        user_session = user_sessions[0]
        user_session.remove()
        return True

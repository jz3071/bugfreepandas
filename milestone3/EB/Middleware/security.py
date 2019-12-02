import jwt
import jwt.jwt.api_jwt as apij
from Context.Context import Context
from time import time
import unicodedata
import logging

_context = Context.get_default_context()


def hash_password(pwd):
    global _context
    h = apij.encode(pwd, key=_context.get_context("JWT_SECRET")).decode('utf-8')
    h = str(h)
    return h


def generate_token(info):

    info["timestamp"] = time()
    email = info['email']

    if email == 'sjtuly1996@gmail.com':
        info['role']='admin'
    else:
        info['role']='usr'

    # What's this???
    # info['created'] = str(info['created'])

    # This .decode('utf-8) is important. Without it, the string will be b'.....'
    h = apij.encode(info, key=_context.get_context("JWT_SECRET")).decode('utf-8')
    h = str(h)

    return h


def authorize(url, method, token, target_usr = None):
    # token = unicode(str, errors='replace')
    info = apij.decode(token, key=_context.get_context("JWT_SECRET"))
    logging.debug("TOKEN INFO: " + str(info))
    auth = None
    if url == "/email":
        if method == "PUT":
            cur_usr = info['email']
            auth = (target_usr == cur_usr)
        elif method == "DELETE":
            role = info['role']
            auth = (role == 'admin')
        else:
            pass
    else:
        pass

    return auth


def ETag(Etag, cur_usr_info):
    cur_Etag = hash_password({"Etag": cur_usr_info})
    return Etag == cur_Etag



# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
import json
# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging
from datetime import datetime

from flask import Flask, Response, request, session

from Context.Context import Context
from Services.CustomerInfo.Users import UsersService as UserService
from Services.RegisterLogin.RegisterLogin import RegisterLoginSvc as RegisterLoginSvc
from Services.Authentication.Authentication import AuthenticationSvc as AuthSvc
import Middleware.security as security
from Middleware.middleware import SimpleMiddleWare as SimpleM
from Middleware.middleware import MWResponse as MWResponse
from functools import wraps
from flask import g, request, redirect, url_for, render_template, make_response

import Middleware.notification as notification_middleware
import Middleware.security as security_middleware


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(request.url)
        print(request.path)
        inputs = log_and_extract_input(demo, {"parameters": None})
        arg = inputs["query_params"]
        form = inputs["form"]
        body = inputs["body"]
        if arg and arg.get("token") or form and form.get("token") or body and body.get("token"):
            return f(*args, **kwargs)
        else:
            return redirect("/login", code=302)
        # print("\nDecorator was called!!!!. Request = ", request)
        # return f(*args, **kwargs)
    return decorated_function


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


###################################################################################################################
#
# AWS put most of this in the default application template.
#
# AWS puts this function in the default started application
# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username


# AWS put this here.
# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'


from Middleware.middleware import SimpleMiddleWare as SimpleM

# EB looks for an 'application' callable by default.
# This is the top-level application that receives and routes requests.
application = Flask(__name__)

# Middleware
application.wsgi_app = SimpleM(application.wsgi_app)


@application.before_request
def before_decorator():
    print(".... In before decorator ...")
    # path = request.path
    # no_need_login_path = ["/favicon.ico", "/login", "/api/login", "/api/registration", "/health", "/test"]
    # if path not in no_need_login_path:
    #     print(request.url)
    #     print(request.path)
    #     inputs = log_and_extract_input(demo, {"parameters": None})
    #     arg = inputs["query_params"]
    #     form = inputs["form"]
    #     body = inputs["body"]
    #     if arg and arg.get("token") or form and form.get("token") or body and body.get("token"):
    #         pass
    #     else:
    #         return redirect("/login", code=302)


@application.after_request
def after_decorator(rsp):
    print("... In after decorator ...")
    return rsp


# add a rule for the index page. (Put here by AWS in the sample)
@application.route("/", methods=["GET"])
@login_required
def init_page():
    return header_text + say_hello() + instructions + footer_text


# add a rule when the page is accessed with a name appended to the site
# URL. Put here by AWS in the sample
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

##################################################################################################################
# The stuff I added begins here.

_default_context = None
_user_service = None
_registration_service = None
_authentication_service = None


def _get_default_context():

    global _default_context

    if _default_context is None:
        _default_context = Context.get_default_context()

    return _default_context


def _get_user_service():
    global _user_service

    if _user_service is None:
        _user_service = UserService(_get_default_context())

    return _user_service


def _get_registration_service():
    global _registration_service

    if _registration_service is None:
        _registration_service = RegisterLoginSvc()

    return _registration_service


def _get_authentication_service():
    global _authentication_service

    if _authentication_service is None:
        _authentication_service = AuthSvc()

    return _authentication_service


def init():

    global _default_context, _user_service

    _default_context = Context.get_default_context()
    _user_service = UserService(_default_context)
    _registration_service = RegisterLoginSvc()

    logger.debug("_user_service = " + str(_user_service))


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):

    path = request.path
    args = dict(request.args)
    forms = dict(request.form)
    data = None
    headers = dict(request.headers)
    method = request.method

    try:
        if request.data is not None:
            data = request.json
        else:
            data = None
    except Exception as e:
        # This would fail the request in a more real solution.
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    inputs =  {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data,
        "form": forms
        }

    log_message += " received: \n" + json.dumps(inputs, indent=2)
    logger.debug(log_message)

    return inputs


def log_response(method, status, data, txt):

    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2, default=str))


# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
@login_required
def health_check():

    rsp_data = { "status": "healthy", "time": str(datetime.now()) }
    rsp_str = json.dumps(rsp_data)
    rsp = MWResponse(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/home", methods=["GET"])
@login_required
def home():

    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    if inputs["method"] == "GET":
        para = inputs["query_params"]
        first_name = None
        last_name = None
        usr_email = None
        token = None
        if 'first_name' in para:
            first_name = para['first_name']
        if 'last_name' in para:
            last_name = para['last_name']
        if 'usr_email' in para:
            usr_email = para['usr_email']
        if 'token' in para:
            token = para['token']
        rsp_data = render_template("homepage.html", first_name=first_name, last_name=last_name,
                                   token=token, usr_email=usr_email)
        rsp_status = 200
        rsp_txt = "OK"
    else:
        rsp_data = None
        rsp_status = 501
        rsp_txt = "NOT IMPLEMENTED"

    if rsp_data is not None:
        full_rsp = make_response(rsp_data)
        full_rsp.statue = rsp_status
        full_rsp.content_type = "text/html"
        # full_rsp = Response(json.dumps(rsp_data, default=str),
        #                     status=rsp_status, content_type="application/json")
    else:
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    return full_rsp


@application.route("/demo/<parameter>", methods=["GET", "POST"])
@login_required
def demo(parameter):

    inputs = log_and_extract_input(demo, { "parameter": parameter })

    msg = {
        "/demo received the following inputs" : inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


@application.route("/api/user/<email>", methods=["GET", "PUT", "DELETE"])
@login_required
def user_email(email):

    global _user_service

    inputs = log_and_extract_input(demo, {"parameters": email})
    logging.debug(inputs)
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        user_service = _get_user_service()
        auth_service = _get_authentication_service()

        logger.debug("/email: _user_service = " + str(user_service))

        if inputs["method"] == "GET":
            rsp = user_service.get_by_email(email)
            if rsp is not None:
                rsp_json = json.dumps(rsp, sort_keys=True)
                logger.debug("RSP_JSON: " + str(rsp_json))

                para = inputs["query_params"]
                usr_first_name = para["usr_first_name"]
                usr_last_name = para["usr_last_name"]
                token = para["token"]
                ETag = security_middleware.hash_password({"Etag": rsp_json})

                first_name = rsp['first_name']
                last_name = rsp['last_name']
                email = rsp['email']
                usrid = rsp['id']
                rsp_data = render_template("profile.html", usr_first_name=usr_first_name,
                                           usr_last_name=usr_last_name,
                                           search_first_name=first_name,
                                           search_last_name=last_name, search_email=email,
                                           search_id=usrid, token=token, ETag=ETag)
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "PUT":

            # update_data = inputs["body"]
            para = inputs["form"]
            token = para["token"]
            update_data = {
                "email": para["new_email"],
                "first_name": para["new_first_name"],
                "last_name": para["new_last_name"],
                "password": para["new_password"]
            }
            logging.debug("PUT DEBUG: " + str(update_data))
            Etag = para["Etag"]

            rsp = auth_service.update(url="/email", target_usr=email, token=token, update_data=update_data, Etag=Etag)
            # rsp = user_service.update_user(=update_data, email=email)
            print(rsp)
            if rsp[0] == "success":
                token = rsp[1]
                first_name = rsp[2]['first_name']
                last_name = rsp[2]['last_name']
                email = rsp[2]['email']
                usrid = rsp[2]['id']

                rsp_json = json.dumps(rsp[2], sort_keys=True)
                logger.debug("RSP_JSON_PUT: " + str(rsp_json))
                new_ETag = security_middleware.hash_password({"Etag": rsp_json})

                rsp_data = render_template("profile.html", usr_first_name=first_name,
                                           usr_last_name=last_name,
                                           search_first_name=first_name,
                                           search_last_name=last_name, search_email=email,
                                           search_id=usrid, token=token, ETag=new_ETag)
                rsp_status = 200
                rsp_txt = "OK"

            elif rsp[0] == "Content Conflict":
                rsp_data = None
                rsp_status = 409
                rsp_txt = "Content Conflict"

            elif rsp[0] == "No authentication":
                rsp_data = None
                rsp_status = 401
                rsp_txt = "No authentication"

            else:
                rsp_data = None
                rsp_status = 403
                rsp_txt = "CANNOT UPDATE"

        elif inputs["method"] == "DELETE":

            para = inputs["form"]
            token = para["token"]
            rsp = auth_service.delete(url="/email", target_usr=email, token=token)

            logger.debug("DELETE RSP: " + str(rsp))

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 403
                rsp_txt = "CANNOT DELETE"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            full_rsp = make_response(rsp_data)
            full_rsp.statue = rsp_status
            full_rsp.content_type = "text/html"
            # full_rsp = Response(json.dumps(rsp_data, default=str),
            #                     status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/registration", methods=["POST"])
def registration():

    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        # logger.error("/api/registration: _r_svc = " + str(r_svc))

        if inputs["method"] == "POST":

            rsp = r_svc.register(inputs['form'])

            if rsp is not None:
                first_name = rsp[1]['first_name']
                last_name = rsp[1]['last_name']
                usr_email = rsp[1]['email']
                token = rsp[0]
                rsp_data = render_template("homepage.html", first_name=first_name, last_name=last_name,
                                           token=token, usr_email=usr_email)
                rsp_status = 201
                rsp_txt = "CREATED"
                link = rsp_data[0]
                auth = rsp_data[1]
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "ALREADY EXISTED"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            # TODO Generalize generating links
            headers = {"Location": "/api/users/" + link}
            headers["Authorization"] =  auth
            full_rsp = make_response(rsp_data)
            full_rsp.headers = headers
            full_rsp.statue = rsp_status
            full_rsp.content_type = "text/html"
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/registration: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/registration", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/login", methods=["POST"])
def login():
    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        logger.error("/api/login: _r_svc = " + str(r_svc))

        if inputs["method"] == "POST":
            rsp = r_svc.login(inputs['form'])

            # If NOT AUTHORIZED, rsp also has value(False)... Maybe we should change it.
            # if rsp is not None:
            if rsp != False:
                first_name = rsp[1]['first_name']
                last_name = rsp[1]['last_name']
                token = rsp[0]
                usr_email = rsp[1]['email']
                rsp_data = render_template("homepage.html", first_name=first_name, last_name=last_name,
                                           token=token, usr_email=usr_email)
                rsp_status = 201
                rsp_txt = "CREATED"

            else:
                rsp_data = None
                rsp_status = 403
                rsp_txt = "NOT AUTHORIZED"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        logger.debug("CHECK RSP STATUS " + str(rsp_status))
        if rsp_data is not None:
            # TODO Generalize generating links
            # It is impossible to get header by js without start a ajax request...
            # So I have to pass the token as a parameter. Maybe we need rewrite the frontend.
            headers = {"Authorization": rsp[0]}
            full_rsp = make_response(rsp_data)
            full_rsp.headers=headers
            full_rsp.statue=rsp_status
            full_rsp.content_type="text/html"
        else:
            full_rsp = Response(json.dumps(rsp_txt, default=str), status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/login: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/login", rsp_status, rsp_data, rsp_txt)

    # This is used to solved cross domain invoke
    # full_rsp.headers['Access-Control-Allow-Origin'] = '*'
    # full_rsp.headers['Access-Control-Allow-Credentials'] = 'false'
    # full_rsp.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    # full_rsp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    print(full_rsp)
    return full_rsp


@application.route("/api/test_middleware/<parameter>", methods=["GET", "PUT", "DELETE", "POST"])
def test_middleware(parameter):

    security_middleware.authorize(request.url, request.method,
                                  request.headers.get("Authorization", None))
    logger.debug("/api/user/<email>" + json.dumps(request, default=str))

    # Other middleware goes here ...

    # Now do the application functions.

    # And now do the functions for post processing the request.
    logger.debug("/api/user/<email>" + json.dumps(request, default=str))
    if request.method in ('POST', 'PUT', 'DELETE'):
        notification_middleware.publish_change_event(request.url, request.json)

    # More stuff goes here.

    return "something"


@application.route("/login", methods=["GET"])
def show_login():
    return render_template("login_register.html")


@application.route("/test", methods=["PUT"])
def test():
    print(request.files)
    inputs = log_and_extract_input(demo, {"parameters": None})
    print(inputs)

    return {"YY":"TT"}


def do_something_before():
    print("\n")
    print("***************** Do something before got ... **************", request)
    print("\n")


def do_something_after(rsp):
    print("\n")
    print("***************** Do something AFTER got ... **************", request)
    print("\n")
    return rsp



logger.debug("__name__ = " + str(__name__))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    application.before_request(do_something_before)
    application.after_request(do_something_after)
    application.run(port=5011)


# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
from flask import Flask, Response, request, jsonify

from datetime import datetime
import json

from CustomerInfo.Users import UsersService as UserService
from Context.Context import Context
from CustomerInfo.SNS_topic import SNS

# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging
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

# EB looks for an 'application' callable by default.
# This is the top-level application that receives and routes requests.
application = Flask(__name__)

# add a rule for the index page. (Put here by AWS in the sample)
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello('yunjie') + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL. Put here by AWS in the sample
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

##################################################################################################################
# The stuff I added begins here.

_default_context = None
_user_service = None
_sns_topic = None


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

def _get_sns_topic():
    global _sns_topic
    if _sns_topic is None:
        _sns_topic = SNS()
        _sns_topic.set_up()
    return _sns_topic

def init():

    global _default_context, _user_service

    _default_context = Context.get_default_context()
    _user_service = UserService(_default_context)

    logger.debug("_user_service = " + str(_user_service))


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):

    path = request.path
    args = dict(request.args)
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
        "body": data
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

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2))


# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():

    rsp_data = { "status": "healthy", "time": str(datetime.now()) }
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "POST"])
def demo(parameter):

    inputs = log_and_extract_input(demo, { "parameter": parameter })
    #logger.debug(inputs['method'])
    msg = {
        "/demo received the following inputs" : inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp

@application.route("/api/login", methods=["POST", "PUT"])
def user_login_register():

    full_rsp = Response('hello', status=200, content_type="text/plain")
    return full_rsp

@application.route("/api/register", methods=["POST", "PUT"])
def user_register():
    if request.method == "POST":
        # initial post
        # curl -i -X POST -H "Content-Type: application/json" -d "{\"last_name\": \"yunjie\", \"first_name\":\"cao\", \"email\":\"yc3702@columbia.edu\", \"password\":\"123456\",\"id\":\"hhhh\"}" http://127.0.0.1:5000/api/register
        inputs = log_and_extract_input(user_register)
        new_user = inputs["body"]
        rsp_data = None
        rsp_status = None
        rsp_txt = None
        global _user_service
        global _sns_topic
        try:
            user_service = _get_user_service()
            _sns_topic = _get_sns_topic()
            rsp = user_service.create_user(new_user, sns=_sns_topic)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "Failed"
            if rsp_data is not None:
                full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
            else:
                full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

        except Exception as e:
            logger.error('Something wrong in registration ' + str(e))
            rsp_status = 500
            rsp_txt = "INTERNAL SERVER ERROR when register user."
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    elif request.method == "PUT":
        # verify users
        inputs = log_and_extract_input(user_register)
        verify_user = inputs["body"]
        rsp_data = None
        rsp_status = None
        rsp_txt = None
        global _user_service
        try:
            user_service = _get_user_service()
            update_info = {'status': 'ACTIVE'}
            template = {'email': verify_user.get('email', None)}
            rsp = user_service.update_user(update_info, template)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "Ok to verify user"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "Failed"
            if rsp_data is not None:
                full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
            else:
                full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

        except Exception as e:
            logger.error('Something wrong in registration ' + str(e))
            rsp_status = 500
            rsp_txt = "INTERNAL SERVER ERROR when verify user."
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    return full_rsp


# @application.route("/api/user/verify/<token>", methods=["GET", "PUT", "DELETE"])
# def verify_user(token):



@application.route("/api/user/<email>", methods=["GET", "PUT", "DELETE"])
def user_email(email):

    global _user_service

    inputs = \
        (demo, { "parameters": email })
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    logger.debug(inputs)
    try:
        user_service = _get_user_service()
        logger.error("/email: _user_service = " + str(user_service))

        if request.method == "GET":
            rsp = user_service.get_by_email(email)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        elif request.method == 'PUT':
            inputs = log_and_extract_input(user_email)
            update_info = inputs["body"]
            rsp_data = None
            rsp_status = 200
            rsp_txt = "OK"
            rsp = user_service.update_user(update_info, {"email":email})
            if rsp is None:
                rsp_data = None
                rsp_status = 400
                rsp_txt = "Update failed"
            else:
                rsp_data = rsp
        elif request.method == "DELETE":
            rsp_data = None
            rsp_status = 200
            rsp_txt = "OK"
            rsp = user_service.delete_user({"email": email})
            if rsp is None:
                rsp_data = None
                rsp_status = 400
                rsp_txt = "Delete failed"
            else:
                rsp_data = rsp

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
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


logger.debug("__name__ = " + str(__name__))
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.


    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    application.run()
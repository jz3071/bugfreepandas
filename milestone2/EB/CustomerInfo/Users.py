from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import UsersRDB as UsersRDB
import json
from CustomerInfo.SNS_topic import SNS
# The base classes would not be IN the project. They would be in a separate included package.
# They would also do some things.

class ServiceException(Exception):

    unknown_error   =   9001
    missing_field   =   9002
    bad_data        =   9003

    def __init__(self, code=unknown_error, msg="Oh Dear!"):
        self.code = code
        self.msg = msg


class BaseService():

    missing_field   =   2001

    def __init__(self):
        pass


class UsersService(BaseService):

    required_create_fields = ['last_name', 'first_name', 'email', 'password', 'id']


    def __init__(self, ctx=None):

        if ctx is None:
            ctx = Context.get_default_context()



    @classmethod
    def get_by_email(cls, email):
        result = UsersRDB.get_by_email(email)
        return result

    @classmethod
    def create_user(cls, user_info, sns=None):
        for f in UsersService.required_create_fields:
            v = user_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field,
                                       "Missing field = " + f)

            if f == 'email':
                if v.find('@') == -1:
                    raise ServiceException(ServiceException.bad_data,
                           "Email looks invalid: " + v)

        user_email =  user_info.get('email', None)
        if user_email is not None and sns is not None:
            sns.client.subscribe(
                TopicArn=sns.topic_arn,
                Protocol='lambda',
                # Endpoint='arn:aws:lambda:us-east-2:086478487177:function:Handler'
                Endpoint='arn:aws:lambda:us-east-2:086478487177:function:lambda_jwt'
            )
            sns.client.publish(Message=json.dumps({'email': user_email}), TopicArn=sns.topic_arn)
        result = UsersRDB.create_user(user_info=user_info)

        return result

    @classmethod
    def update_user(cls, update_info, template):
        result = UsersRDB.update_user(update_info, template)
        return result

    @classmethod
    def delete_user(cls, template):
        result = UsersRDB.delete_user(template)
        return result



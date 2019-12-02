import Middleware.security as security
from Context.Context import Context
from Services.CustomerInfo.Users import UsersService as user_svc
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class RegisterLoginSvc():

    _context = None

    @classmethod
    def set_context(cls, ctx):
        RegisterLoginSvc._context = ctx

    @classmethod
    def get_data_object(cls):
        return None

    @classmethod
    def get_context(cls):
        if cls._context is None:
            cls.set_context(Context.get_default_context())
        return cls._context


    @classmethod
    def register(cls, data):

        hashed_pw = security.hash_password({"password" : data['password']})
        data["password"] = hashed_pw
        try:
            result = user_svc.create_user(data)
            s_info = user_svc.get_by_email(data['email'])
            tok = security.generate_token(s_info)
            return tok, s_info
        except:
            return None



    @classmethod
    def login(cls, login_info):
        # Why hash that? Is that password informal?
        test = security.hash_password({"password" : login_info['password']})
        # test = login_info['password']
        logger.debug("LOGIN_INFO" + str(test))
        s_info = user_svc.get_by_email(login_info['email'])
        logger.debug("SLOGIN_INFO" + str(s_info))
        test = str(test)
        if s_info and str(test) == s_info['password']:
            tok = security.generate_token(s_info)
            return tok, s_info
        else:
            return False

    @classmethod
    def get_field_map(cls, target_resource):
        pass







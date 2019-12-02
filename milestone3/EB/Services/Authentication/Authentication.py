import Middleware.security as security
from Context.Context import Context
from Services.CustomerInfo.Users import UsersService as user_svc
import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class AuthenticationSvc():

    _context = None

    @classmethod
    def set_context(cls, ctx):
        AuthenticationSvc._context = ctx

    @classmethod
    def get_data_object(cls):
        return None

    @classmethod
    def get_context(cls):
        if cls._context is None:
            cls.set_context(Context.get_default_context())
        return cls._context


    @classmethod
    def update(cls, url, target_usr, token, update_data, Etag):
        auth = security.authorize(url=url, method="PUT", token=token, target_usr=target_usr)
        logger.debug("auth: " + str(auth))
        if auth:
            cur_usr_info = user_svc.get_by_email(target_usr)
            cur_usr_info = json.dumps(cur_usr_info, sort_keys=True)
            logger.debug("cur_usr_info: " + str(cur_usr_info))

            etag = security.ETag(Etag=Etag, cur_usr_info=cur_usr_info)
            if etag:
                hashed_pw = security.hash_password({"password": update_data['password']})
                update_data["password"] = hashed_pw

                logger.debug("************" + str(update_data["password"]))

                try:
                    result = user_svc.update_user(update_data, target_usr)
                    s_info = user_svc.get_by_email(update_data['email'])
                    tok = security.generate_token(s_info)
                    return "success", tok, s_info
                except:
                    return "exception", None, None
            else:
                return "Content Conflict", None, None
        else:
            return "No authentication", None, None


    @classmethod
    def delete(cls, url, target_usr, token):
        auth = security.authorize(url=url, method="DELETE", token=token, target_usr=target_usr)
        logger.debug("auth: " + str(auth))

        if auth:
            try:
                result = user_svc.delete_user(target_usr)
                return result
            except:
                return None
        else:
            return None







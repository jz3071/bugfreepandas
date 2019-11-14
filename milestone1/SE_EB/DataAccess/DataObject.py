from abc import ABC, abstractmethod

import pymysql.err

import DataAccess.DataAdaptor as data_adaptor


class DataException(Exception):
    unknown_error = 1001
    duplicate_key = 1002

    def __init__(self, code=unknown_error, msg="Something awful happened."):
        self.code = code
        self.msg = msg


class BaseDataObject(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def create_instance(cls, data):
        pass


class UsersRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def get_by_email(cls, email):

        sql = "select * from e6156.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=email, fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def create_user(cls, user_info):

        result = None

        try:

            sql, args = data_adaptor.create_insert(table_name="users", row=user_info)
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = user_info['email']


        except pymysql.err.IntegrityError as ie:
            print(ie)
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            log_msg = "DataObjectCreate_user: Exception = " + str(e)
            print(log_msg)
            raise DataException()

        return result

    @classmethod
    def delete_user(cls, email):

        sql = "delete from e6156.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=email, fetch=True)
        if res:
            res = "Successful delete"
        else:
            res = "Failed"

        return res

    @classmethod
    def update_user(cls, user_info, email):

        sql, arg = data_adaptor.create_update(table_name="users", new_values=user_info, template={'email': email})
        res, data = data_adaptor.run_q(sql=sql, args=arg, fetch=True)
        if res:
            res = "Successful update"
        else:
            res = "Failed"

        return res

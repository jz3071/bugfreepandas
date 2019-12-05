import DataAccess.DataAdaptor as data_adaptor
from abc import ABC, abstractmethod
import pymysql.err
import Middleware.security as middleware_security

class DataException(Exception):

    unknown_error   =   1001
    duplicate_key   =   1002

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

class ProfileEntriesRDB(BaseDataObject):

    @classmethod
    def get_profile(cls, param_id):
        # Only get the user not deleted
        sql = "select * from e6156.profile_entries where profile_entry_id=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(param_id), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None

        return result

    @classmethod
    def get_profile_query(cls, param_id):
        # Only get the user not deleted
        sql = "select * from e6156.profile_entries where user_id=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(param_id), fetch=True)
        if data is not None and len(data) > 0:
            result =  data
        else:
            result = None

        return result
    @classmethod
    def get_user_profile(cls, params, fields):

        sql, args = data_adaptor.create_select(table_name="profile_entries", template=params, fields=fields)
        res, data = data_adaptor.run_q(sql, args)

        if data is not None and len(data) > 0:
            result = data
        else:
            result = None

        return result

    @classmethod
    def create_profile_entry(cls, entries):

        result = None

        try:
            sql, args = data_adaptor.create_insert(table_name="profile_entries", row=entries)
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = entries['user_id']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def delete_profile(cls, profile_id):
        result = None

        sql, args = data_adaptor.create_select(table_name="profile_entries", template={"profile_entry_id": profile_id})
        _, prev_data = data_adaptor.run_q(sql, args)

        if prev_data is not None and len(prev_data) > 0:
            sql, args = data_adaptor.delete(table_name="profile_entries", template={"profile_entry_id": profile_id})
            result, _ = data_adaptor.run_q(sql, args)
            if result != 1:
                result = None
        else:
            return result

        return "Completed"


    @classmethod
    def update_profile(cls, param_profile, update_template, data):
        result = None
        conn = None
        cursor = None

        try:
            conn = data_adaptor._get_default_connection()
            cursor = conn.cursor()

            # a wrapper function helps to pass params
            def run_q(sql_, args_):
                return data_adaptor.run_q(sql_, args_, cur=cursor, conn=conn, commit=False)

            sql, args = data_adaptor.create_select(table_name="profile_entries", template=update_template)

            _, prev_data = run_q(sql, args)

            if prev_data is not None and len(prev_data) > 0:

                sql, args = data_adaptor.create_update(table_name="profile_entries",
                                                       new_values=data,
                                                       template=update_template)
                res, _ = run_q(sql, args)
                if res != 1:
                    raise Exception('cannot update data!')
                else:
                    # get new Etag
                    new_data = prev_data[0]
                    for k, v in data.items():
                        new_data[k] = v
                    result = new_data['profile_entry_id']
         
                conn.commit()
            else:
                raise Exception('cannot retrieve data')

        except Exception as e:
            # rollback
            conn.rollback()
            raise e
        finally:
            # closing database connection.
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return result

import threading
from threading import current_thread
import DataAccess.DataAdaptor as data_adaptor

threadlocal = threading.local()

# TODO: We should read this information from the environment.
default_connect_info =  {
    'host': 'localhost',
    'port': 3306,
    'user': 'yunjie',
    'password': 'Cc08234494',
    'db': 'se',
    'charset': 'utf8'
}


def t1():

    current_thread().default_connect_info  = default_connect_info
    # print(default_connect_info)
    data_adaptor.get_connection(default_connect_info)

t1()

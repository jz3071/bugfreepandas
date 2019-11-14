import copy


class Context():

    def __init__(self, inital_ctx=None):
        self._context = inital_ctx

    def get_context(self, ctx_name):
        result = self._context.get(ctx_name, None)
        return result

    def set_context(self, ctx_name, ctx):
        self._context[ctx_name] = copy.deepcopy(ctx)

    @classmethod
    def get_default_context(cls):
        # db_connect_info = os.environ['db_connect_info']
        # db_connect_info = json.loads(db_connect_info)
        # db_connect_info = {'host': 'localhost',
        #                    'user': 'root',
        #                    'password': 'Ly1239233008',
        #                    'port': 3306,
        #                    'db': 'e6156'}

        db_connect_info = {'host': 'sedatabase.ccrfnreg6ro1.us-east-1.rds.amazonaws.com',
                           'user': 'yangli',
                           'password': 'columbialiyang',
                           'port': 3306,
                           'db': 'e6156'}

        ctx = {"db_connect_info": db_connect_info}

        result = Context(ctx)
        return result

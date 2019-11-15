
from CustomerInfo.Users import UsersService as UserService
import json
from uuid import uuid4
def t1():

    r = UserService.get_by_email('metus.vitae@nibhAliquamornare.edu')
    print("Result = \n", json.dumps(r, indent=2))



def t2():

    user = {
        "last_name": "Gamgee",
        "first_name": "Sam",
        "id": str(uuid4()),
        "email": "sg@shore.gov",
        "password": "cat"
    }

    r = UserService.create_user(user)
    print("Result = ", r)


#t1()
t2()
# -*- coding: utf-8 -*-
# @Time    : 2019/11/29 8:43
# @Author  : Yunjie Cao
# @FileName: Address.py
# @Software: PyCharm
# @Email   ：YunjieCao@hotmail.com

import requests
from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_zipcode import Lookup
import boto3


class SmartyStreet():
    def __init__(self):
        pass


class AddressService():
    def __init__(self):
        context = {
            'smarty_streets_id': 'your id',
            'smarty_streets_token': 'your token',
            'aws_access_key_id': "your id",
            'aws_secret_access_key': "your_key"
        }

        self.dynamodb = boto3.client('dynamodb',
                              aws_access_key_id=context["aws_access_key_id"],
                              aws_secret_access_key=context["aws_secret_access_key"],
                              region_name="us-east-2")

        self._auth_id = context['smarty_streets_id']
        self._auth_token = context['smarty_streets_token']

        # This set up the credentials for the SDK
        self._credentials = StaticCredentials(self._auth_id, self._auth_token)

        # We will use the SDK for looking up zipcodes.
        self._zip_client = ClientBuilder(self._credentials).build_us_zipcode_api_client()

        # I am going to use the "raw" rest API for address lookup to provide a comparison of
        # the two API approaches. Also, I should be getting the URL for the context.
        self._address_lookup_url = "https://us-street.api.smartystreets.com/street-address"

    def validate_address(self, address):
        url = self._address_lookup_url
        params = {}
        params['auth-id'] = self._auth_id
        params['auth-token'] = self._auth_token
        params['street'] = address['street']

        addressee = address.get('addressee', None)
        if addressee is not None:
            params['addressee'] = addressee

        state = address.get('state', None)
        if state is not None:
            params['state'] = state

        city = address.get('city', None)
        if city is not None:
            params['city'] = city

        zipcode = address.get('zipcode', None)
        if zipcode is not None:
            params['zipcode'] = zipcode

        result = requests.get(url, params=params)

        # We need to handle the various status codes. We will learn this when we study REST.
        if result.status_code == 200:
            # If we got more than one address, then there was something wrong and the address into is imprecise
            j_data = result.json()
            if len(j_data) > 1:
                rsp = None
            else:
                rsp = j_data[0]['components']
                rsp['deliver_point_barcode'] = j_data[0]['delivery_point_barcode']
        else:
            rsp = None
        return rsp

    def create_address(self, addr):
        """
        validate first, if not valid, return None
        insert the information to the DynamoDB
        return address-id
        :param addr: address information passed by POST request
        :return: the status of the POST execution
        """
        rsp = self.validate_address(addr)
        if rsp is None:
            return None
        addr_id = rsp['deliver_point_barcode']
        encoded_addr = self.encode_addr(addr)
        encoded_addr['addr_id'] = {'S': addr_id}
        put_res = self.dynamodb.put_item(TableName='address', Item=encoded_addr)
        if put_res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return addr_id
        else:
            return None

    def get_address(self, address_id):
        """
        get address information from dynamodb
        :param address_id: address id
        :return: None(failure) or address information in json
        """
        ret = self.dynamodb.get_item(TableName='address', Key={'addr_id': {'S': address_id}})
        get_res = ret.get('Item', None)
        if get_res is not None:
            get_res = self.decode_addr(get_res)
        return get_res

    def update_address(self, address_id, new_address):
        """
        verify the updated address first,
        then update addresss information in dynamodb
        :param address_id: current address_id
        :param new_address: updated address
        :return: status of update
        """
        rsp = self.validate_address(new_address)
        if rsp is None:
            return None
        new_addr_id = rsp['deliver_point_barcode']
        new_addr = self.encode_addr(new_address)
        try:
            try:
                self.dynamodb.delete_item(TableName='address', Key={'addr_id': {'S': address_id}})
            except Exception:
                pass
            new_addr['addr_id'] = {'S': new_addr_id}
            self.dynamodb.put_item(TableName='address', Item=new_addr)
            return new_addr_id
        except Exception:
            return None

    def encode_addr(self, addr):
        encoded_addr = {}
        for k, v in addr.items():
            encoded_addr[k] = {'S': v}
        return encoded_addr

    def decode_addr(self, addr):
        decoded_addr = {}
        for k, v in addr.items():
            decoded_addr[k] = v['S']
        return decoded_addr

# def create_table(addr):
#     client = boto3.client('dynamodb',
#             aws_access_key_id="AKIAJROULLEUX2SFIUJA",
#             aws_secret_access_key="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",
#             region_name="us-east-2")
#     processed_addr = {}
#     for k,v in addr.items():
#         processed_addr[k] = {'S': v}
#     processed_addr['addr_id'] = {'S': '950142083017'}
#     res = client.put_item(TableName='address', Item=processed_addr)
#     ret = client.get_item(TableName='address', Key={'addr_id':{'S':'950142083017'}})
#     try:
#         delete_res = client.delete_item(TableName='address', Key={'addr_id': {'S': '950142083017'}})
#         processed_addr['addr_id']['S'] = '123456'
#         update_res = client.put_item(TableName='address', Item=processed_addr)
#     except Exception:
#         pass
#     print(ret)
#     print(res)
#     print(update_res)

if __name__ == "__main__":
    test_address = AddressService()
    addr = {
        "addressee": "Apple Inc",
        'street': '1 infinite loop',
        'state': 'CA',
        'city': 'cupertino',
        'zipcode': '95014'
    }
    # # test_address.validate_address(addr)
    # create_table(addr)
    print(test_address.update_address('123456', addr))
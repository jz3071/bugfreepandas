# -*- coding: utf-8 -*-
# @Time    : 2019/11/7 9:33
# @Author  : Yunjie Cao
# @FileName: SNS_topic.py
# @Software: PyCharm
# @Email   ：YunjieCao@hotmail.com

import boto3
import json

class SNS():
    def __init__(self):
        pass

    def create_client(self):
        client = boto3.client(
            "sns",
            aws_access_key_id="AKIAJ2KUDXFALXYVJ4BQ",
            aws_secret_access_key="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",
            region_name="us-east-2"
        )
        self.client = client

    def create_topic(self):
        self.topic = self.client.create_topic(Name="Notifications")
        self.topic_arn = self.topic['TopicArn']

    def set_up(self):
        self.create_client()
        self.create_topic()

    def subscribe(self):
        self.client.subscribe(
            TopicArn=self.topic_arn,
            Protocol='lambda',
            # Endpoint='arn:aws:lambda:us-east-2:086478487177:function:Handler'
            Endpoint='arn:aws:lambda:us-east-2:086478487177:function:lambda_jwt'
        )
        self.client.publish(Message=json.dumps({'email':'yc3702'}), TopicArn=self.topic_arn)


if __name__=="__main__":
    test = SNS()
    test.create_client()
    test.create_topic()
    test.subscribe()

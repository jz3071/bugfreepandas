# # -*- coding: utf-8 -*-
# # @Time    : 2019/11/7 11:35
# # @Author  : Yunjie Cao
# # @FileName: lambda.py
# # @Software: PyCharm
# # @Email   ：YunjieCao@hotmail.com

import json
import boto3
from botocore.exceptions import ClientError
import jwt.jwt.api_jwt as apij
import botocore.vendored.requests as requests
import logging
# import requests

# Note: The logging levels should come from a config/property file and not be hard coded.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)

_secret = "secret"


def respond(err, res=None):
    """

    TODO: We need to flesh this out to handle other error conditions, and to
        return the necessary CORS headers for options.

    :param err: The error that occurred.
    :param res: The response body in JSON.
    :return: A properly formatted API Gateway response.
    """
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    hashed_email = event.get("queryStringParameters", None)
    
    if hashed_email is None: # deal with registration
        logger.info("\nEvent = " + json.dumps(event, indent=2) + "\n")
        user_info = event.get("Records", None)
        if user_info is None:
            user_info = {'nmd': 'why'}
        else:
            logger.info("###################" + json.dumps(user_info[0], indent=2))
            user_info = user_info[0]["Sns"]["Message"]
            user_info = json.loads(user_info)
        test_stuff = user_info
        logger.info("Encoding " + json.dumps(test_stuff))
        tok = apij.encode(test_stuff, key=_secret)
        logger.info("Encoded = " + str(tok))
        dec = apij.decode(tok, key=_secret)
        logger.info("Decoded =  " + json.dumps(dec))
    
        # Some introspection of event allows figuring out where it came from.
        records = event.get("Records", None)
        method = event.get("httpMethod", None)
    
        if records is not None:
            logger.info("I got an SNS event.")
            logger.info("Records = " + json.dumps(records))
        elif method is not None:
            logger.info("I got an API GW proxy event.")
            logger.info("\nhttpMethod = " + method + "\n")
        else:
            logger.info("Not sure what I got.")
    
        response = respond(None, {"status": 'send an email, please verify'})
        send_email_to_user(tok)
        
    else: # deal with verification
        hashed_res = hashed_email.get("name", None)
        if hashed_res is not None:
            verified_user = apij.decode(hashed_res, key=_secret)
            logger.info("test in verification "+ json.dumps(verified_user))
            verfied_res = requests.put("http://E6156se-env.u8p2cj2wmp.us-east-2.elasticbeanstalk.com/api/register", json = verified_user)
            
            logger.info("send a request to app.py")
            response = respond(None, {'status': 'Successfully verify!'})
            
    return response


def send_email_to_user(token):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "YunjieCao@hotmail.com"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = "yc3702@columbia.edu"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-west-2"

    # The subject line for the email.
    SUBJECT = "Please verify your account of Fantasy Baseball"
    
    hashed_token = token.decode('utf-8')

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Thank you for registration.\r\n"
                 "Click here to activate. "
                 )

    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Thank you for registration</h1>
      <p>Click  <a href='https://p8df4935m4.execute-api.us-east-2.amazonaws.com/default/lambda_jwt/?name=""" + hashed_token + """'>here</a> to activate.
        </p>
    </body>
    </html>
                """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          aws_access_key_id="AKIAJ2KUDXFALXYVJ4BQ",
                          aws_secret_access_key="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",
                          region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line

        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
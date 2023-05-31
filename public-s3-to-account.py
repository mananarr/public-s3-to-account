import argparse
import boto3
import json
from botocore.exceptions import ClientError

def policy_document(account_id):
    policy = {"Version": "2012-10-17",
        "Statement": [{
                "Sid": "AllowResourceAccount",
                "Effect": "Allow","Action": ["s3:ListBucket","s3:GetObject"],"Resource": "*",
                "Condition": {"StringLike": {"s3:ResourceAccount": account_id + "*"}}}]}

    return policy


def assume_role(role_arn, policy, client):
    try:
        assume_role = client.assume_role(RoleArn=role_arn, RoleSessionName='session', Policy=policy)
        session_id = assume_role["Credentials"]["AccessKeyId"]
        session_key = assume_role["Credentials"]["SecretAccessKey"]
        session_token = assume_role["Credentials"]["SessionToken"]
        session = boto3.Session(aws_access_key_id = session_id,aws_secret_access_key = session_key,aws_session_token = session_token)
    except Exception as e:
        print('error in assume role operation: ', str(e))
        session = None
 
    return session 

def calculate_id(role_arn, config_type, resource, client, debug):
    testing_digits = ""
    for i in range(0, 12):
        success = 0
        for j in range(0, 10):
            if debug == 1:
                if len(testing_digits) < 11:
                    print('Testing with: ' + testing_digits + str(j) + "*")
                else:
                    print('Testing with: ' + testing_digits + str(j))
            policy_input = testing_digits + str(j)
            policy = policy_document(policy_input)
            session = assume_role(role_arn, json.dumps(policy), client)
            if session is not None:
                s3_client = session.client('s3')
                if config_type == 'bucket':
                    try:
                        s3_client.head_bucket(Bucket=resource)
                        success = 1
                        if debug == 1:
                            print('\u001b[1m\u001b[32mSuccessful\033[0m')
                    except ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            return "Invalid Bucket"
                        elif debug == 1:
                            print(e.response['Error']['Code'], e.response['Error']['Message'])
                else:
                    try:
                        bucket,key = resource.split('/', 1)
                        s3_client.head_object(Bucket=bucket, Key=key)
                        success = 1
                        if debug == 1:
                            print('\u001b[1m\u001b[32mSuccessful\033[0m')
                    except ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            return "Invalid Object"
                        elif debug == 1:
                            print(e.response['Error']['Code'], e.response['Error']['Message'])
                if success == 1:
                    testing_digits = policy_input
                    break
        else:
            break
    return testing_digits


def main():

    parser = argparse.ArgumentParser(description='CLI Input Example')

    parser.add_argument('-role', '--role_arn', type=str, help='ARN of the Role to be assumed', required=True)
    parser.add_argument('-resource', '--resource', type=str, help='Comma separated bucket  names / object paths', required=True)
    parser.add_argument('-profile', '--profile', type=str, help='Name of the aws cli profile to use')
    parser.add_argument('-debug', '--debug', type=int, help='Comma separated object paths along with bucket names')

    args = parser.parse_args()

    role_arn = args.role_arn

    resources = args.resource.split(',')
    debug = args.debug
    profile = args.profile
    if profile is None:
        profile = 'default'
    buckets = []
    objects = []
    for i in resources:
        if '/' in i:
            objects.append(i)
        else:
            buckets.append(i)


    session = boto3.Session(profile_name=profile)
    client = session.client('sts')

    for bucket in buckets:
        print('\nEnumerating Account ID for bucket: ' + bucket + '\n')
        account_id = calculate_id(role_arn, 'bucket', bucket, client, debug)
        if account_id == "":
            account_id = "Not Found"
        print('AWS Account Id: ' + "\u001b[1m" + account_id + "\033[0m")

    for object_path in objects:
        print('\nEnumerating Account ID for object: ' + object_path + '\n')
        account_id = calculate_id(role_arn, 'object', object_path, client, debug)
        if account_id == "":
            account_id = "Not Found"
        print('AWS Account Id: ' + "\u001b[1m" +  account_id + "\033[0m")

if __name__ == "__main__":
    main()
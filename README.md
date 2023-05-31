# Public S3 to Account ID

A python script to enumerate the AWS Account ID from a Public S3 bucket/object.

# Setup

1. Create a role with following permissions and make note of the ARN of the role to be used later:
```
{
    "Version": "2012-10-17", "Statement": [{"Sid": "Statement1","Effect": "Allow",
            "Action": ["s3:ListBucket","s3:GetObject"],"Resource": "*"}]
}
```
2. To its Trust Relationship, add permission for your user to assume the role:
```
{
    "Version": "2012-10-17",
    "Statement": [{"Sid": "Statement1","Effect": "Allow","Principal": {"AWS": "arn:aws:iam::XXXXXXXXXXXX:user/username"},
            "Action": "sts:AssumeRole"}]
}
```
3. Make sure your user has permission to assume the role, if not sure, create the following policy and attach to the user:
```
{
    "Version": "2012-10-17",
    "Statement": [{"Sid": "VisualEditor0","Effect": "Allow","Action": "sts:AssumeRole","Resource": "arn:aws:iam::XXXXXXXXXXXX:role/role"}]
}
```


# Usage

```
$ python3 public-s3-to-account.py -role <assume_role_arn> -resource <public_bucket_name>
$ python3 public-s3-to-account.py -role <assume_role_arn> -resource <public_object_path_with_bucket_name>
$ python3 public-s3-to-account.py -role <assume_role_arn> -resource bucket1,bucket2,object1,object2 -debug 1
$ python3 public-s3-to-account.py -role <assume_role_arn> -resource bucket1,bucket2,object1,object2 -debug 1 -profile <awscli_profile>
```

import json
import boto3
s3 = boto3.client("s3")

def lambda_handler(event, context):
    detail = event["detail"]
    event_name = detail["eventName"]
    if event_name != "DeleteBucketPublicAccessBlock":
        raise ValueError(f"Unsupported event: {event_name}")
    bucket_name = detail["requestParameters"]["bucketName"]
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )
    result = {"eventName": event_name, "remediatedBucket": bucket_name, "status": "RESTORED"}
    print(json.dumps(result))
    return result
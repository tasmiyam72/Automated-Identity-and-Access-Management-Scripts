import boto3

def get_secret(key: str, WithDecryption: bool = True):
    print(f"Fetching secret: {key}")
    client = boto3.client("ssm")
    resp = client.get_parameter(Name=key, WithDecryption=True)
    return resp["Parameter"]["Value"]


def get_secret_with_session(key: str, session):
    client = boto3.client(
        "ssm",
        aws_access_key_id=session[0],
        aws_secret_access_key=session[1],
        aws_session_token=session[2],
    )
    resp = client.get_parameter(Name=key, WithDecryption=True)
    return resp["Parameter"]["Value"]
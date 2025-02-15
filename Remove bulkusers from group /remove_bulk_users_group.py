import json
import requests
import msal
import boto3


def get_secret(key: str, WithDecryption: bool = True):
    client = boto3.client("ssm")
    resp = client.get_parameter(Name=key, WithDecryption=True)
    return resp["Parameter"]["Value"]

client_id= " "
client_secret= " "
tenant_id= " "
GRAPH_API_URL ="https://graph.microsoft.com/.default"
GROUP_ID= " "


def get_access_token(client_id, client_secret, tenant_id, GRAPH_API_URL):
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )
    result = app.acquire_token_for_client(scopes=[GRAPH_API_URL])
    if "access_token" in result:
        return result["access_token"]
    else:
        print(f"Failed to obtain token: {result.get('error')}, {result.get('error_description')}")
        return None

def get_user_id(object_id, token):
    url = f"https://graph.microsoft.com/v1.0/users/{object_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)

    print(f"Checking user: {object_id} - Status: {response.status_code}")
    print(response.text)  # Debugging output

    if response.status_code == 200:
        return object_id  
    return None

def remove_user_from_group(user_id, token):
    url = f"https://graph.microsoft.com/v1.0/groups/{GROUP_ID}/members/{user_id}/$ref"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)

    return response.status_code in [204, 404]  # 204: Success, 404: Already removed



def bulk_remove_users(users, token):
    if isinstance(users, str):  # If a file path is passed
        with open(users, "r") as file:
            users = file.read().splitlines()

    for email in users:
        user_id = get_user_id(email.strip(), token)
        if user_id:
            if remove_user_from_group(user_id, token):
                print(f"Removed: {email}")
            else:
                print(f"Failed to remove: {email}")
        else:
            print(f"User not found: {email}")


if __name__ == "__main__":
    graph_token = get_access_token(client_id, client_secret, tenant_id, GRAPH_API_URL)
    
    if not graph_token:
        print("Error: Unable to get access token. Exiting...")
        exit(1)

    bulk_remove_users("users.txt", graph_token)

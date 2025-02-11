import os

import boto3
import msal
import requests


def get_secret(key: str, WithDecryption: bool = True):
    client = boto3.client("ssm")
    resp = client.get_parameter(Name=key, WithDecryption=True)
    return resp["Parameter"]["Value"]


DSO_CLIENT_ID = get_secret(os.environ["CLIENT_ID"])
DSO_CLIENT_SECRET = get_secret(os.environ["CLIENT_SECRET"])
TENANT_ID = os.environ["TENANT_ID"]
SCOPE = "https://graph.microsoft.com/.default"


def azure_ad_access_token(
    DSO_CLIENT_ID: str, DSO_CLIENT_SECRET: str, TENANT_ID: str, SCOPE: str
):
    app = msal.ConfidentialClientApplication(
        DSO_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=DSO_CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=[SCOPE])
    if "access_token" in result:
        return result["access_token"]
    else:
        print(
            f"Failed to obtain token: {result.get('error')}, {result.get('error_description')}"
        )
        return None


# Delete App Registrations
def delete_app_registrations(app_ids, token):
    headers = {"Authorization": f"Bearer {token}"}
    for app_id in app_ids:
        url = f"https://graph.microsoft.com/v1.0/applications/{app_id}"
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Successfully deleted app with ID: {app_id}")
        else:
            print(
                f"Failed to delete app with ID: {app_id}, Response: {response.status_code}, {response.text}"
            )


if __name__ == "__main__":
    graph_token = azure_ad_access_token(
        DSO_CLIENT_ID=DSO_CLIENT_ID,
        DSO_CLIENT_SECRET=DSO_CLIENT_SECRET,
        TENANT_ID=TENANT_ID,
        SCOPE="https://graph.microsoft.com/.default",
    )

    header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {graph_token}",
        "ConsistencyLevel": "eventual",
    }

    app_registration_ids = [
        " ",  # Add the object ID of app reg
    ]
    try:
        delete_app_registrations(app_registration_ids, graph_token)
    except Exception as e:
        print(f"Error: {e}")

import pandas as pd
import requests
import argparse
from ssm import get_secret_with_session

TOKENS: dict = {}


def get_api_token(tenant: str, session):
    secret_path = f"/okta/iam/api-token/kpmg-uk.oktapreview.com"
    api_token = get_secret_with_session(secret_path, session)
    print(f"API token fetched for {tenant}")
    return api_token


def retrieve_api_token(tenant: str, session, tokens=TOKENS) -> str:
    if tenant not in TOKENS:
        print(f"No cache found for: {tenant}")
        token = get_api_token(tenant, session)
        cache_token(tenant, token)

    return TOKENS[tenant]


def set_token(token: str, tokens=TOKENS) -> None:
    tokens["current"] = token
    print("API token set for the current thread")


def cache_token(tenant: str, token: str, tokens=TOKENS) -> None:
    tokens[tenant] = token
    print(f"API token cached for {tenant}")


def request_okta(url: str, request_type: str = "GET"):
    # api_token = tokens["current"]
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "SSWS 00t3lKi7v-PXtKl4akAfA-TLEjqrRPvijND3_ypQc2",
    }
    return requests.request(request_type, url, headers=headers)


def get_user_status(user_id: str, user_email: str) -> str:
    print(f"Retrieving status of {user_id} from tenant")
    url = f"https://kpmg-uk.oktapreview.com/api/v1/users/{user_id}"
    resp = request_okta(url)
    if resp.status_code == 200:
        if user_email.lower() == resp.json()["profile"]["email"].lower():
            print(
                f"SUCCESS: User {user_email} with User-ID {user_id} found in tenant"
            )
            print(
                f"User {user_email} with User-ID {user_id} status: {resp.json()['status']}"
            )
            return resp.json()["status"]
        else:
            print(
                f"FAILURE: User {user_email.lower()} email is not matching with API response email: {resp.json()['profile']['email'].lower()}"
            )
    elif resp.status_code == 404:
        print(f"FAILURE: User {user_email} with User-ID {user_id} not found in tenant")
    else:
        print(f"ERROR: {resp.text}. Tenant: tenant")


def deactivate_user(user_id, user_email) -> int:
    url = f"https://kpmg-uk.oktapreview.com/api/v1/users/{user_id}/lifecycle/deactivate"
    resp = request_okta(url, "POST")
    if resp.status_code == 200:
        print("deactivated the user")
    elif resp.status_code == 404:
        print(f"FAILURE: User {user_email} with User-ID {user_id} not found in tenant")
    else:
        print("Unsupoorted action")
    return resp.status_code


def delete_user(user_id: str, user_email: str) -> int:
    print(f"Deleting User {user_email} with User-ID {user_id} from tenant")
    url = f"https://kpmg-uk.oktapreview.com/api/v1/users/{user_id}"
    status = get_user_status(user_id, user_email)
    if status == None:
        return print(
            f"FAILURE: User {user_email} is not deleted due to email mismatch between RedShift and API response."
        )
    elif status != "DEPROVISIONED":
        deactivate_user(user_id, user_email)

    resp = request_okta(url, "DELETE")
    if resp.status_code == 204:
        print(
            f"SUCCESS: User {user_email} with User-ID {user_id} deleted from tenant"
        )
    elif resp.status_code == 404:
        print(
            f"FAILURE: User {user_email} with User-ID {user_id} not found in tenant"
        )
    else:
        print(f"ERROR: {resp.text}. Tenant: tenant")

    return resp.status_code


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--action", help="Action", required=False, default="check"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = read_args()
    action = args.action
    csv = pd.read_csv("Testuser.csv")
    for index, row in csv.iterrows():
        user_id = row["user_id"]
        user_email = row["user_email"]
        print(user_id, user_email)
        deactivate_user(user_id, user_email)
        delete_user(user_id, user_email)

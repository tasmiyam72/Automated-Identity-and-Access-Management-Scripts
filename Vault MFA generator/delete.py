import os
import requests
import time
import hvac
from pprint import pprint
from dotenv import load_dotenv
from logger import get_logger

load_dotenv(verbose=True)

logger = get_logger("okta-mfa", level=os.environ.get("LOG_LEVEL", "INFO"))

def get_vault_client():
    """
    Authenticates to Vault and create a session
    """
    client = hvac.Client(url=os.environ["VAULT_URL"])
    client.token = os.environ["VAULT_TOKEN"]
    if not client.is_authenticated():
        raise ValueError(f"Invalid vault credentials")
    logger.info("Vault client created")
    return client


def list_all_vault_totp_keys(vault_client: hvac.Client, mount_point: str = "okta-mfa") -> list:
    vault_url = os.environ["VAULT_URL"]
    request_url = f"{vault_url}/v1/{mount_point}/keys"
    request_header = {"X-Vault-Token": vault_client.token}

    response = requests.request("LIST", request_url, headers=request_header)

    if response.status_code == 200:

        return response.json()
    else:
        return []


def delete_vault_totp(vault_client: hvac.Client, vault_totp_key: str, mount_point: str = "okta-mfa") -> bool:
    vault_url = os.environ["VAULT_URL"]
    request_url = f"{vault_url}/v1/{mount_point}/keys/{vault_totp_key}"
    request_header = {"X-Vault-Token": vault_client.token}

    response = requests.request("DELETE", request_url, headers=request_header)

    time.sleep(2.5)

    if response.status_code in (200, 204):
        return True
    else:
        return False


vault_client = get_vault_client()

list_of_all_vault_totp_keys = list_all_vault_totp_keys(vault_client)

for vault_keys in list_of_all_vault_totp_keys["data"]["keys"]:
    delete_keys = delete_vault_totp(vault_client, vault_keys)

    if delete_keys:
        pprint("DELETED")
    else:
        pprint("FAILED TO DELETE")

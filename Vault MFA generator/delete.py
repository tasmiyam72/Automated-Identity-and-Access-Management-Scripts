import time
from pprint import pprint
import hvac
import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv(verbose=True)

VAULT_URL = "https://vault.customappsteam.co.uk"
MOUNT_POINT = "okta-mfa"
ROLE_ID = " "
SECRET_ID = ""

def vault_authentication_client():
    vault_client = hvac.Client(url=VAULT_URL, strict_http=True)
    vault_client.auth.approle.login(role_id=ROLE_ID, secret_id=SECRET_ID)
    logger.info(f"Is the client authenticated: {vault_client.is_authenticated()}")
    if vault_client.is_authenticated():
        logger.info("vault app role is valid")
    else:
        raise ValueError("invalid or missing vault token")
    return vault_client


def list_all_vault_totp_keys(
    vault_client: hvac.Client, vault_url, mount_point: str
) -> list:
    request_url = f"{vault_url}/v1/{mount_point}/keys"
    request_header = {"X-Vault-Token": vault_client.token}
    response = requests.request("LIST", request_url, headers=request_header)
    pprint(response.text)
    if response.status_code == 200:
        pprint(response.text.json())
        return response.json()["data"]["keys"]
    else:
        return []


def delete_vault_totp(
    vault_client: hvac.Client, vault_totp_key: str, vault_url: str, mount_point: str
) -> bool:
    request_url = f"{vault_url}/v1/{mount_point}/keys/{vault_totp_key}"
    request_header = {"X-Vault-Token": vault_client.token}
    response = requests.request("DELETE", request_url, headers=request_header)
    time.sleep(2.5)
    if response.status_code in (200, 204):
        return True
    else:
        return False


def main():
    vault_client = vault_authentication_client()
    list_of_all_vault_totp_keys = list_all_vault_totp_keys(
        vault_client, VAULT_URL, MOUNT_POINT
    )
    for vault_keys in list_of_all_vault_totp_keys:
        delete_keys = delete_vault_totp(vault_client, vault_keys, VAULT_URL)
        if delete_keys:
            logger.info("keys deleted")
        else:
            logger.info("failed to delete")


if __name__ == "__main__":
    main()
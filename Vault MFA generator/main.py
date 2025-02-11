import os
import hvac
import requests
import time
from dotenv import load_dotenv
from loguru import logger
from utils import read_vault_secret, list_vault_secrets

load_dotenv(verbose=True)

VAULT_TOKEN = os.environ["VAULT_TOKEN"]
VAULT_URL = os.environ["VAULT_ADDR"]
MOUNT_POINT = os.environ["MOUNT_POINT"]
TARGET_FOLDER = os.environ["TARGET_FOLDER"]

def get_vault_client():
    """
    Authenticates to Vault and create a session
    """
    client = hvac.Client(url=VAULT_URL)
    client.token = VAULT_TOKEN
    if not client.is_authenticated():
        raise ValueError(f"Invalid vault credentials")
    logger.info("Vault client created")
    return client


def list_tenant_folders(
     vault_client
) -> list:
    tenant_list = list_vault_secrets(
        vault_client,TARGET_FOLDER, MOUNT_POINT)
    
    return tenant_list["data"]["keys"]


def clean_tenant_list(tenant_list: list) -> list:
    for tenant_id in tenant_list:
        if "/" not in tenant_id:
            tenant_list.remove(tenant_id)
            logger.info("%s removed from list", tenant_id)
    return tenant_list


def get_breakglass_folders(
    tenant_list, vault_client
) -> list:
    for tenant_name in tenant_list:
        vault_path = TARGET_FOLDER + "/" + tenant_name
        breakglass_folders = list_vault_secrets(
            vault_client, vault_path, MOUNT_POINT)
        for folder in breakglass_folders["data"]["keys"]:
            yield f"{vault_path}{folder}"


def read_breakglass_secrets(
    breakglass_folders, vault_client
):
    list_of_secret_dicts = []
    for bg_path in breakglass_folders:
        secret_dicts = read_vault_secret(
             vault_client, bg_path, MOUNT_POINT)
        list_of_secret_dicts.append(secret_dicts)
    return list_of_secret_dicts
   

def process_secrets_dictionaries(secrets_dict: dict) -> list:
    mfa_secret_match = []
    username_match = []
    for dictionary in secrets_dict:
        if "mfa_secret_key" in dictionary:
            mfa_secret_match.append(dictionary["mfa_secret_key"])
            username_match.append(dictionary["username"])
            
        elif "mfa_secret" in dictionary:
            mfa_secret_match.append(dictionary["mfa_secret"])
            username_match.append(dictionary["username"])

        else:
            print("nope")
    mfa_secret_list = zip(mfa_secret_match, username_match)

    return list(mfa_secret_list)
    


def list_all_vault_totp_keys(
    vault_client
) -> list:
    request_url = f"{VAULT_URL}/v1/{MOUNT_POINT}/{TARGET_FOLDER}"
    request_header = {"X-Vault-Token": vault_client.token}

    response = requests.request("LIST", request_url, headers=request_header)

    if response.status_code == 200:
        return response.json()["data"]["keys"]
    
    return []


def create_vault_mfa_key(
    vault_client,
    mfa_secret_values,
    list_of_keys: list,
    vault_path: str = VAULT_URL,
) -> str:
    vault_url = vault_path
    for mfa_info in mfa_secret_values:
        mfa_secret_value = mfa_info[0]
        username = mfa_info[1]
        tenant_name = str(mfa_info[1]).split("@")[1]
        request_url = f"{vault_path}/v1/okta-mfa/keys/{username}"
        request_header = {"X-Vault-Token": vault_client.token}
        request_payload_url = f"otpauth://okta-mfa/{tenant_name}:{username}?secret={mfa_secret_value}&issuer=Microsoft"
        request_payload = {"url": request_payload_url}
        if username not in list_of_keys:
            time.sleep(2.5)
            response = requests.post(
                request_url, json=request_payload, headers=request_header
            )
            if response.status_code in (200, 204):
                logger.info(f"created totp key for {username}")
            else:
                logger.info(f"failed to create totp key for {username}")
        else:
            logger.info(f"totp key for {username} already exists")


if __name__ == "__main__":
    vault_client = get_vault_client()
    list_of_all_vault_totp_keys = list_all_vault_totp_keys(vault_client)
    okta_tenants = list_tenant_folders(vault_client)
    tenant_list = clean_tenant_list(okta_tenants)
    breakglass_folders = get_breakglass_folders(tenant_list, vault_client)
    breakglass_secrets = read_breakglass_secrets(breakglass_folders,vault_client)
    mfa_secret_values = process_secrets_dictionaries(breakglass_secrets)
    create_vault_mfa_key(vault_client,mfa_secret_values,list_of_keys=list_of_all_vault_totp_keys)

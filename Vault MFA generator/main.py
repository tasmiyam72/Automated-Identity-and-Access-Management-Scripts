import os
import time
import hvac
import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv(verbose=True)

VAULT_TOKEN = os.environ["VAULT_TOKEN"]
VAULT_URL = os.environ["VAULT_ADDR"]
MOUNT_POINT_SECRETS = os.environ["MOUNT_POINT_SECRETS"]
MOUNT_POINT_TOTP = os.environ["MOUNT_POINT_TOTP"]
TARGET_FOLDER = os.environ["TARGET_FOLDER"]
TOTP_ISSUER = os.environ["TOTP_ISSUER"]


def vault_authentication_client() -> hvac.Client:
    vault_client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN, strict_http=True)
    logger.info(f"Is the client authenticated: {vault_client.is_authenticated()}")
    if vault_client.is_authenticated():
        logger.info("token is valid")
        return vault_client
    raise ValueError("invalid or missing vault token")


TARGET_FOLDER = os.environ["TARGET_FOLDER"]
TOTP_ISSUER = os.environ["ISSUER"]


def list_vault_secrets(vault_client, path: str, mount_point: str):
    return vault_client.secrets.kv.v2.list_secrets(path=path, mount_point=mount_point)


def list_tenant_folders(
    vault_client: hvac.Client, vault_folder: str, mount_point: str
) -> list:
    tenant_list = list_vault_secrets(
        vault_client=vault_client, path=vault_folder, mount_point=mount_point
    )
    return tenant_list["data"]["keys"]


def clean_tenant_list(tenant_list: list) -> list:
    for tenant_id in tenant_list:
        if "/" not in tenant_id:
            tenant_list.remove(tenant_id)
            logger.info(f"{tenant_id} removed from list")
    return tenant_list


def get_breakglass_folders(
    vault_folder: str, tenant_list: list, vault_client: hvac.Client, mount_point: str
) -> list:
    for tenant_id in tenant_list:
        tenant_folder = vault_folder + "/" + tenant_id
        breakglass_folders = list_vault_secrets(
            vault_client=vault_client, path=tenant_folder, mount_point=mount_point
        )
        for bg_folder in breakglass_folders["data"]["keys"]:
            yield f"{tenant_folder}{bg_folder}"


def read_breakglass_secrets(
    breakglass_folders, vault_client: hvac.Client, mount_point: str
):
    list_of_secret_dicts = []
    for bg_path in breakglass_folders:
        secret_dicts = read_vault_secret(
            vault_client=vault_client,
            vault_path=bg_path,
            mount_point=mount_point,
        )
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


def read_vault_secret(
    vault_client: hvac.Client, vault_path: str, mount_point: str
) -> dict:
    try:
        read_secret_response = vault_client.secrets.kv.v2.read_secret_version(
            path=vault_path, mount_point=mount_point
        )["data"]
        return read_secret_response["data"]
    except hvac.exceptions.Forbidden as forbidden_exception:
        logger.error(forbidden_exception.errors)
    except hvac.exceptions.InvalidPath as invalid_exception:
        logger.error(invalid_exception.url)


def list_all_vault_totp_keys(
    vault_client: hvac.Client, vault_url: str, mount_point: str
) -> list:
    request_url = f"{vault_url}/v1/{mount_point}/keys"
    request_header = {"X-Vault-Token": vault_client.token}
    response = requests.request("LIST", request_url, headers=request_header)
    if response.status_code == 200:
        return response.json()["data"]["keys"]
    return []


def create_vault_mfa_key(
    vault_client: hvac.Client,
    mfa_secret_list: tuple,
    list_of_keys: list,
    vault_url: str,
    mount_point: str,
    issuer: str,
) -> str:
    for mfa_info in mfa_secret_list:
        mfa_secret_value = mfa_info[0]
        username = mfa_info[1]
        tenant_name = str(mfa_info[1]).split("@")[1]
        request_url = f"{vault_url}/v1/{mount_point}/keys/{username}"
        request_header = {"X-Vault-Token": vault_client.token}
        request_payload_url = f"otpauth://{mount_point}/{tenant_name}:{username}?secret={mfa_secret_value}&issuer={issuer}"
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


def main():
    vault_client = vault_authentication_client()
    tenants = list_tenant_folders(vault_client, TARGET_FOLDER, MOUNT_POINT_SECRETS)
    tenant_list = clean_tenant_list(tenants)
    breakglass_folders = get_breakglass_folders(
        TARGET_FOLDER, tenant_list, vault_client, MOUNT_POINT_SECRETS
    )
    breakglass_secrets = read_breakglass_secrets(
        breakglass_folders, vault_client, MOUNT_POINT_SECRETS
    )
    mfa_secret_values = process_secrets_dictionaries(breakglass_secrets)
    vault_totp_keys = list_all_vault_totp_keys(vault_client)
    create_vault_mfa_key(
        vault_client,
        mfa_secret_values,
        vault_totp_keys,
        VAULT_URL,
        MOUNT_POINT_TOTP,
        TOTP_ISSUER,
    )


if __name__ == "__main__":
    main()
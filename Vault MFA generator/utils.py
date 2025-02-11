import boto3
import hvac
from loguru import logger


def list_vault_secrets(vault_client, path: str, mount_point: str):
    return vault_client.secrets.kv.v2.list_secrets(path=path, mount_point=mount_point)


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

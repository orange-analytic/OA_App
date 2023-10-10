"""Azure Key Vault integration."""

import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def get_secret(secret_name: str) -> str:
    return str(
        SecretClient(
            vault_url=os.environ["KEY_VAULT_URI"],
            credential=DefaultAzureCredential(exclude_shared_token_cache_credential=True),
        )
        .get_secret(secret_name)
        .value
    )

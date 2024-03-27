from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class Secret_Manager:
    @staticmethod
    def create_secret_client(keyVaultName):
        credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True)
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        print(f"Creating Secret Client for Azure Key Vault: {keyVaultName}.")
        return SecretClient(vault_url=KVUri, credential=credential)


    @staticmethod
    def retrieve_aoai_client_secrets(secretClient):
        print("Retrieving Azure OpenAI Client Configuration.")
        azure_deployment = secretClient.get_secret("openai-deployment").value
        azure_endpoint = secretClient.get_secret("openai-api-base").value
        api_key = secretClient.get_secret("openai-api-key").value
        api_version = secretClient.get_secret("openai-api-version").value
        return azure_deployment, azure_endpoint, api_key, api_version


    @staticmethod
    def retrieve_ado_secrets(secretClient):
        # ADO Secrets
        print("Retrieving ADO Secrets.")
        pat = secretClient.get_secret("ado-pat").value
        adoOrg = secretClient.get_secret("ado-org").value
        adoProject = secretClient.get_secret("ado-project").value
        return pat, adoOrg, adoProject
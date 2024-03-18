import base64
import os
import sys
import requests
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from bs4 import BeautifulSoup


def create_secret_client(keyVaultName):
    credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True)
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    print(f"Creating Secret Client for Azure Key Vault: {keyVaultName}.")
    return SecretClient(vault_url=KVUri, credential=credential)


def create_azure_openai_client(secretClient):
    print("Creating Azure OpenAI Client.")
    # Azure OpenAI Client Configuration
    return AzureOpenAI(
        azure_deployment=secretClient.get_secret("openai-deployment").value,
        azure_endpoint=secretClient.get_secret("openai-api-base").value,
        api_key=secretClient.get_secret("openai-api-key").value,
        api_version=secretClient.get_secret("openai-api-version").value,
    )


def retrieve_ado_secrets(secretClient):
    # ADO Secrets
    pat = secretClient.get_secret("ado-pat").value
    adoOrg = secretClient.get_secret("ado-org").value
    adoProject = secretClient.get_secret("ado-project").value
    return pat, adoOrg, adoProject


def retrieve_work_item_ids(pat, adoOrg, adoProject):
    authorization = str(base64.b64encode(bytes(":" + pat, "ascii")), "ascii")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + authorization,
    }
    query = {
        "query": "Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.Id] = 4215"
    }
    url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/wiql?api-version=7.1-preview.2"
    response = requests.post(url, headers=headers, body=query)

    IDS = []
    error = False
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        IDS = []
        if data["queryType"] == "flat":
            features = data["workItems"]
        elif data["queryType"] == "oneHop":
            features = [feature["target"] for feature in data["workItemRelations"]]
        for feature in features:
            IDS.append(feature["id"])
        # Remove duplicates using set()
        IDS = list(set(IDS))
    else:
        # Print the error message
        print(
            "Request to connect to ADO failed with status code:", response.status_code
        )
        print("Error message:", response.text)
        error = True
    return IDS, error


def retrieve_work_item_content(IDS, pat, adoOrg, adoProject):
    authorization = str(base64.b64encode(bytes(":" + pat, "ascii")), "ascii")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + authorization,
    }
    payload = {"ids": IDS, "fields": ["System.Title", "System.Description"]}
    url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/workitemsbatch?api-version=7.0"
    response = requests.post(url, headers=headers, json=payload)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        data = response.json()
        content = ""
        for workitem in data["value"]:
            content += "Feature: " + workitem["fields"]["System.Title"] + "\n"
            try:
                soup = BeautifulSoup(
                    workitem["fields"]["System.Description"], "html.parser"
                )
                span = soup.find("span")
                content += "Description: " + span.text + "\n"
            except:
                pass
        print(
            "---------------"
            + "\n"
            + "Release Notes will be generated using this content:"
            + "\n"
            + content
            + "--------------"
        )
    else:
        # Print the error message
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)
    return content


def generate_release_notes(content):
    response = azureOpenAIClient.chat.completions.create(
        model=GPT4T_1106_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a marketing technical writer"},
            {
                "role": "user",
                "content": "Write release notes for this product without using bullet points and all in one paragraph: system capable of generating results from its input",
            },
            {
                "role": "assistant",
                "content": "We are releasing a new product capable of generating output from the input provided in such a way that it helps users",
            },
            {"role": "user", "content": content},
        ],
        temperature=0.1,
        max_tokens=4096,
    )
    print("Release notes:")
    print(response["choices"][0]["message"]["content"])
    # Write release notes to file
    file = open("release_notes.txt", "a")
    file.write(response["choices"][0]["message"]["content"])


def main():
    # 1) Retrieve secrets from Azure Key Vault
    keyVaultName = os.getenv("KEY_VAULT_NAME")
    keyVaultSecretClient = create_secret_client(keyVaultName)
    azureOpenAIClient = create_azure_openai_client(keyVaultSecretClient)
    pat, adoOrg, adoProject = retrieve_ado_secrets(keyVaultSecretClient)

    # 2) Retrieve the ID for the ADO work items with which the Release Notes will be created using an ADO query
    IDS, error = retrieve_work_item_ids(pat, adoOrg, adoProject)

    # 3) Retrieve the Titles and Descriptions of the ADO work items using the ID
    if not error:
        content = retrieve_work_item_content(IDS, pat, adoOrg, adoProject)

        # 4) Send Prompt to OpenAI API using the Titles and Descriptions of the ADO work items
        generate_release_notes(content)
    else:
        print("error")


if __name__ == "__main__":
    main()

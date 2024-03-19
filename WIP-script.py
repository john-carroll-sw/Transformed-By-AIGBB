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


def build_ado_url_and_headers(adoOrg, adoProject, pat, api_version):
    url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/wiql?api-version={api_version}"
    authorization = str(base64.b64encode(bytes(":" + pat, "ascii")), "ascii")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + authorization,
    }
    return url, headers


def retrieve_child_work_item_ids(url, headers, engagementWorkItemId):
    payload = {
        "query": f"""
            SELECT [System.Id], [System.Title], [System.WorkItemType] 
                FROM WorkItemLinks 
                WHERE (
                    [Source].[System.Id] = '{engagementWorkItemId}' AND 
                    [System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward') 
                ORDER BY [System.Id] 
                MODE (Recursive)
        """
    }
    response = requests.post(url, headers=headers, json=payload)

    IDS = []
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data["queryType"] == "tree":
            for relation in data["workItemRelations"]:
                if relation["rel"] == "System.LinkTypes.Hierarchy-Forward":
                    target_id = relation["target"]["id"]
                    IDS.append(target_id)
        # Remove duplicates using set()
        IDS = list(set(IDS))
    else:
        # Print the error message
        print(
            "Request to connect to ADO failed with status code:", response.status_code
        )
        print("Error message:", response.text)
    return IDS


def retrieve_engagement_work_item_content(url, headers, engagementWorkItemId):
    payload = {
        "query": f"Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.Id] = {engagementWorkItemId}"
    }
    response = requests.post(url, headers=headers, json=payload)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        data = response.json()
        content = ""
        # for workItem in data["value"]:
        #     content += "Feature: " + workItem["fields"]["System.Title"] + "\n"
        #     try:
        #         soup = BeautifulSoup(
        #             workItem["fields"]["System.Description"], "html.parser"
        #         )
        #         span = soup.find("span")
        #         content += "Description: " + span.text + "\n"
        #     except:
        #         pass
        print(
            "---------------"
            + "\n"
            + "Customer Story will be generated using this content:"
            + "\n"
            + "Engagement: "
            + content
            + "---------------"
        )
    else:
        # Print the error message
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)
    return content


def retrieve_child_work_item_content(url, headers, IDS):
    # Refer to the WIQL Documentation for more information:
    # https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops
    payload = {
        "query": f"Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.Id] in {IDS}"
    }
    response = requests.post(url, headers=headers, json=payload)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        data = response.json()
        content = ""
        # for workItem in data["value"]:
        #     content += "Feature: " + workItem["fields"]["System.Title"] + "\n"
        #     try:
        #         soup = BeautifulSoup(
        #             workItem["fields"]["System.Description"], "html.parser"
        #         )
        #         span = soup.find("span")
        #         content += "Description: " + span.text + "\n"
        #     except:
        #         pass
        print(
            "---------------"
            + "\n"
            + "Customer Story will be generated using this content:"
            + "\n"
            + content
            + "--------------"
        )
    else:
        # Print the error message
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)
    return content


def generate_customer_story(azureOpenAIClient, model, content):
    response = azureOpenAIClient.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a marketing technical writer"},
            {
                "role": "user",
                "content": "Write a customer story using this content",
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
    print("Customer Story:")
    print(response["choices"][0]["message"]["content"])
    # Write customer story to file
    file = open("customer_story.txt", "a")
    file.write(response["choices"][0]["message"]["content"])


def main():
    # 1) Retrieve secrets from Azure Key Vault
    keyVaultName = os.getenv("KEY_VAULT_NAME")
    keyVaultSecretClient = create_secret_client(keyVaultName)
    azureOpenAIClient = create_azure_openai_client(keyVaultSecretClient)
    pat, adoOrg, adoProject = retrieve_ado_secrets(keyVaultSecretClient)
    wiql_api_version = "7.1-preview.2"
    url, headers = build_ado_url_and_headers(adoOrg, adoProject, pat, wiql_api_version)

    # 2) Retrieve content from the Customer Engagement Work Item
    engagementWorkItemId = "1353"
    engagementContent = retrieve_engagement_work_item_content(
        url, headers, engagementWorkItemId
    )

    # 3) Retrieve the ID's for the ADO work items that are children of the Customer Engagement Work Item
    IDS = retrieve_child_work_item_ids(url, headers, engagementWorkItemId)

    # 4) Retrieve the content from the related ADO work items
    content = retrieve_child_work_item_content(url, headers, IDS)

    # # 5) Send Prompt to OpenAI AP
    # model = keyVaultSecretClient.get_secret("openai-model").value
    # generate_customer_story(azureOpenAIClient, model, content)


if __name__ == "__main__":
    main()

import base64
import json
import os
import sys
import requests
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from Classes.Activity import Activity
from Classes.Engagement import Engagement


def create_secret_client(keyVaultName):
    credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True)
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    print(f"Creating Secret Client for Azure Key Vault: {keyVaultName}.")
    return SecretClient(vault_url=KVUri, credential=credential)


def retrieve_aoai_client_secrets(secretClient):
    print("Retrieving Azure OpenAI Client Configuration.")
    azure_deployment = secretClient.get_secret("openai-deployment").value
    azure_endpoint = secretClient.get_secret("openai-api-base").value
    api_key = secretClient.get_secret("openai-api-key").value
    api_version = secretClient.get_secret("openai-api-version").value
    return azure_deployment, azure_endpoint, api_key, api_version


def retrieve_ado_secrets(secretClient):
    # ADO Secrets
    print("Retrieving ADO Secrets.")
    pat = secretClient.get_secret("ado-pat").value
    adoOrg = secretClient.get_secret("ado-org").value
    adoProject = secretClient.get_secret("ado-project").value
    return pat, adoOrg, adoProject


def create_azure_openai_client(azure_deployment, azure_endpoint, api_key, api_version):
    print("Creating Azure OpenAI Client.")
    return AzureOpenAI(
        azure_deployment=azure_deployment,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version,
    )


def build_ado_url_by_id(adoOrg, adoProject, api_version, workItemId):
    # ADO URL and Headers for single work item request, workItemId is the ID of the work item
    print("Building ADO URL and Headers for single work item request.")
    url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/workitems/{workItemId}?{api_version}"
    return url


def build_ado_url_by_wiql(adoOrg, adoProject, api_version):
    # ADO URL and Headers for WIQL request,  body is the WIQL query
    print("Building ADO URL and Headers for WIQL request.")
    url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/wiql?api-version={api_version}"
    return url


def build_ado_url_batch(adoOrg, adoProject, api_version):
    # ADO URL and Headers for batch request, body is a list of work item ID's and fields to return
    print("Building ADO URL and Headers for batch request.")
    url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/workitemsbatch?api-version={api_version}"
    return url


def create_ado_headers(pat):
    authorization = str(base64.b64encode(bytes(":" + pat, "ascii")), "ascii")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + authorization,
    }
    return headers


def retrieve_related_work_item_ids(url, headers, engagementWorkItemId):
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

    ids = []
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data["queryType"] == "tree":
            for relation in data["workItemRelations"]:
                if relation["rel"] == "System.LinkTypes.Hierarchy-Forward":
                    target_id = relation["target"]["id"]
                    ids.append(target_id)
        # Remove duplicates using set()
        ids = list(set(ids))
    else:
        # Print the error message
        print(
            "Request to connect to ADO failed with status code:", response.status_code
        )
        print("Error message:", response.text)
    return ids


def retrieve_engagement_content(url, headers):
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse the response JSON
        engagementContent = str(Engagement(data))  # Extract the required fields
        content = (
            "------------------------------\n"
            + "Customer Story will be generated using the engagement and the activities' content:\n\n"
            + "---------------\n"
            + "Engagement Information: \n"
            + engagementContent
            + "---------------\n"
        )
        print(content)
    else:
        # Print the error message
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)
    return content


def retrieve_activity_content(url, headers, activityIds):
    payload = {
        "ids": activityIds
    }
    response = requests.post(url, headers=headers, json=payload)
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse the response JSON
        content = str(Activity(data))  # Extract the required fields
        print(+"Activity Information: \n" + content + "---------------\n")
    else:
        # Print the error message
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)
    return content


def generate_customer_story(azureOpenAIClient, model, content):
    # TODO invoke function for prompt compression using LLMLingua: https://github.com/microsoft/LLMLingua

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
    # TODO Return, then send story to sharepoint page


def main():
    # It all starts with a story ;) - The Customer Engagement Work Item.
    # TODO Retrieve this ID from some Call to Action: button click -> api call -> runs this function, provides the work item id.
    engagementWorkItemId = "1353"
    # 4215, 1353

    # 1) Retrieve secrets from Azure Key Vault
    keyVaultName = os.getenv("KEY_VAULT_NAME")
    keyVaultSecretClient = create_secret_client(keyVaultName)
    azure_deployment, azure_endpoint, api_key, api_version = (
        retrieve_aoai_client_secrets(keyVaultSecretClient)
    )
    azureOpenAIClient = create_azure_openai_client(
        azure_deployment, azure_endpoint, api_key, api_version
    )
    pat, adoOrg, adoProject = retrieve_ado_secrets(keyVaultSecretClient)
    headers = create_ado_headers(pat)
    wiql_api_version = "7.0"

    # 2) Retrieve content from the Customer Engagement Work Item
    singleWiUrl = build_ado_url_by_id(adoOrg, adoProject, wiql_api_version, engagementWorkItemId)
    engagementContent = retrieve_engagement_content(singleWiUrl, headers)

    # 3) Retrieve the ID's for the ADO work items that are children of the Customer Engagement Work Item
    relatedWiUrl = build_ado_url_by_wiql(adoOrg, adoProject, wiql_api_version)
    relatedWorkItemsIds = retrieve_related_work_item_ids(relatedWiUrl, headers, engagementWorkItemId)
    print(relatedWorkItemsIds)

    # 4) Retrieve the content from the related ADO work items
    batchWiUrl = build_ado_url_batch(adoOrg, adoProject, pat, wiql_api_version)
    content = retrieve_activity_content(batchWiUrl, headers, relatedWorkItemsIds)

    # 5) Send Prompt to Azure OpenAI API
    # model = keyVaultSecretClient.get_secret("openai-model").value
    # generate_customer_story(azureOpenAIClient, model, content)


if __name__ == "__main__":
    main()

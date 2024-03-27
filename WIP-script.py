import os

from openai import AzureOpenAI
from backend import Secret_Manager
from backend import ADO_Utilities


def create_azure_openai_client(azure_endpoint, api_key, api_version):
    print("Creating Azure OpenAI Client.")
    return AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version,
    )

def generate_customer_story(azureOpenAIClient, azure_deployment, content):
    # TODO invoke function for prompt compression using LLMLingua: https://github.com/microsoft/LLMLingua

    response = azureOpenAIClient.chat.completions.create(
        model=azure_deployment,
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

    ado_metaprompt = ''
    # It all starts with a story ;) - The Customer Engagement Work Item.
    # TODO Retrieve this ID from some Call to Action: button click -> api call -> runs this function, provides the work item id.
    engagementWorkItemId = "3428"

    # 1) Retrieve secrets from Azure Key Vault
    keyVaultName = os.getenv("KEY_VAULT_NAME")
    keyVaultSecretClient = Secret_Manager.create_secret_client(keyVaultName)
    azure_deployment, azure_endpoint, api_key, api_version = (Secret_Manager.retrieve_aoai_client_secrets(keyVaultSecretClient))
    azureOpenAIClient = create_azure_openai_client(azure_endpoint, api_key, api_version)
    pat, adoOrg, adoProject = Secret_Manager.retrieve_ado_secrets(keyVaultSecretClient)
    headers = ADO_Utilities.create_ado_headers(pat)
    wiql_api_version = "7.0"

    # 2) Retrieve content from the Customer Engagement Work Item
    engagementWIContent = ADO_Utilities.retrieve_engagement_content(adoOrg, adoProject, wiql_api_version, engagementWorkItemId, headers)
    ado_metaprompt += engagementWIContent

    # 3) Retrieve the ID's for the ADO work items that are children of the Customer Engagement Work Item
    relatedWiUrl = ADO_Utilities.build_ado_url_by_wiql(adoOrg, adoProject, wiql_api_version)
    relatedWorkItemsIds = ADO_Utilities.retrieve_related_work_item_ids(relatedWiUrl, headers, engagementWorkItemId)
    # print(relatedWorkItemsIds)

    # 4) Retrieve the content from the related ADO work items
    activityContent = ADO_Utilities.retrieve_activity_content(adoOrg, adoProject, wiql_api_version, headers, relatedWorkItemsIds)
    ado_metaprompt += activityContent

    # 5) Send Prompt to Azure OpenAI API
    # model = keyVaultSecretClient.get_secret("openai-model").value
    # generate_customer_story(azureOpenAIClient, azure_deployment, content)

    print(ado_metaprompt)

if __name__ == "__main__":
    main()

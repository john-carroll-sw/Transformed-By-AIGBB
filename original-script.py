# Peter Kowalchuk. 2023

import os
import sys
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

import requests
import base64
import os
from bs4 import BeautifulSoup
import openai

# 1) Retrieve secrets from Azure Key Vault
if len(sys.argv)==2:
    credential=os.system("az login")
    keyVaultName = sys.argv[1]
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True)
    client = SecretClient(vault_url=KVUri, credential=credential)
    print(f"Retrieving secrets from Azure Key Vault: {keyVaultName}.")
    # OpenAI Secrets
    openai.api_type = client.get_secret("openai-api-type").value 
    openai.api_version = client.get_secret("openai-api-version").value 
    openai.api_base = client.get_secret("openai-api-base").value 
    openai.api_key = client.get_secret("openai-api-key").value 
    #ADO Secrets
    pat = client.get_secret("ado-pat").value 
    adoOrg = client.get_secret("ado-org").value 
    adoProject = client.get_secret("ado-project").value 
    queryId = client.get_secret("ado-query-id").value 
    credential = os.system("az logout")
else:
    print("Missing Argument in python script execution call: Provide the name of your Azure Key Vault resource as an argument")
    exit()

# 2) Retrive the ID for the ADO work items with which the Release Notes will be created using an ADO query
authorization = str(base64.b64encode(bytes(':'+pat, 'ascii')), 'ascii')
headers = {
    'Accept': 'application/json',
    "Content-Type": "application/json",
    'Authorization': 'Basic '+authorization
}
url = "https://dev.azure.com/"+adoOrg+"/"+adoProject+"/_apis/wit/wiql/"+queryId+"?api-version=7.0"
print("Establishing connection to ADO")
response = requests.get(url, headers=headers)
IDS=[]
error=False
# Check if the request was successful
if response.status_code == 200:
    print("Retrieving work items from ADO")
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
    print("Request to connect to ADO failed with status code:", response.status_code)
    print("Error message:", response.text)
    error=True

# 3) Retrieve the Titles and Descriptions of the ADO work items using the ID
if not error:
    print("Release Notes will be generated using the following ADO work items: " + str(IDS))
    # Make the API request - get the work items
    payload = {
    "ids": IDS,
    "fields": [
        "System.Title",
        "System.Description"
    ]
    }
    url = "https://dev.azure.com/"+adoOrg+"/"+adoProject+"/_apis/wit/workitemsbatch?api-version=7.0"
    response = requests.post(url, headers=headers, json=payload)
    # Check if the request was successful
    if response.status_code == 200:
        print("Retriving Tittle and Description from the ADO work items")
        # Parse the response JSON
        data = response.json()
        content=''
        for workitem in data['value']:
            content+="Feature: "+workitem['fields']['System.Title']+"\n"
            try:
                soup = BeautifulSoup(workitem['fields']['System.Description'], 'html.parser')
                span = soup.find('span')
                content+="Description: "+span.text+"\n"
            except:
                pass
        print("---------------"+"\n"+"Release Notes will be generated using this content:"+"\n"+content+"--------------")
    else:
        # Print the error message
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)

    # 4) Send Prompt to OpenAI API using the Tittles and Descriptions of the ADO work items
    print("Sending prompt to OpenAI")
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo", # The deployment name you chose when you deployed the ChatGPT or GPT-4 model.
        messages=[
            {"role": "system", "content": "You are a marketing technical writer"},
            {"role": "user", "content": "Write release notes for this product without using bullet points and all in one paragraph: system capable of generating results from its input"},
            {"role": "assistant", "content": "We are releasing a new product capable of generating output from the input provided in such a way that it helps users"},
            {"role": "user", "content": content}
        ]
    )
    print("Release notes:")
    print(response['choices'][0]['message']['content'])
    # Write release notes to file
    file = open("release_notes.txt", "a")
    file.write(response['choices'][0]['message']['content'])
else:
    print("error")
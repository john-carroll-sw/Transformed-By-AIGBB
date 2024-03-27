import base64
import requests

from classes.Comment import Comment
from classes.Activity import Activity
from classes.Engagement import Engagement


class ADO_Utilities:
    @staticmethod
    def build_ado_url_by_id(adoOrg, adoProject, api_version, workItemId):
        # ADO URL for single work item request, workItemId is the ID of the work item
        print("Building ADO URL for single work item request.")
        url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/workitems/{workItemId}?{api_version}"
        return url

    @staticmethod
    def build_ado_url_for_comments(adoOrg, adoProject, workItemId):
        # ADO URL for comments request, workItemId is the ID of the work item
        # print("Building ADO URL for comments request.")
        url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/workitems/{workItemId}/comments?api-version=7.1-Preview"
        return url

    @staticmethod
    def build_ado_url_by_wiql(adoOrg, adoProject, api_version):
        # ADO URL for WIQL request,  body is the WIQL query
        print("Building ADO URL for WIQL request.")
        url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/wiql?api-version={api_version}"
        return url

    @staticmethod
    def build_ado_url_batch(adoOrg, adoProject, api_version):
        # ADO URL for batch request, body is a list of work item ID's and fields to return
        print("Building ADO URL for batch request.")
        url = f"https://dev.azure.com/{adoOrg}/{adoProject}/_apis/wit/workitemsbatch?api-version={api_version}"
        return url

    @staticmethod
    def create_ado_headers(pat):
        authorization = str(base64.b64encode(bytes(":" + pat, "ascii")), "ascii")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Basic " + authorization,
        }
        return headers

    @staticmethod
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
                "Request to connect to ADO failed with status code:",
                response.status_code,
            )
            print("Error message:", response.text)
        return ids

    @staticmethod
    def retrieve_engagement_content(
        adoOrg, adoProject, wiql_api_version, engagementWorkItemId, headers
    ):
        engagementContent = ""
        singleWiUrl = ADO_Utilities.build_ado_url_by_id(
            adoOrg, adoProject, wiql_api_version, engagementWorkItemId
        )
        response = requests.get(singleWiUrl, headers=headers)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse the response JSON
            engagementContent = str(Engagement(data))  # Extract the required fields
            engagementContent = (
                "------------------------------\n"
                + "Customer Story will be generated using the engagement and the activities' content:\n\n"
                + "---------------\n"
                + "Engagement Information: \n"
                + engagementContent
                + "---------------\n"
            )
            # print(engagementContent)
        else:
            # Print the error message
            print("Request failed with status code:", response.status_code)
            print("Error message:", response.text)

        # Retrieve comments content
        commentsContent = ADO_Utilities.retrieve_comments_content(
            adoOrg, adoProject, engagementWorkItemId, headers
        )
        if commentsContent:
            engagementContent += "Comments: \n" + commentsContent
        return engagementContent

    @staticmethod
    def retrieve_activity_content(
        adoOrg, adoProject, wiql_api_version, headers, activityIds
    ):
        activityContent = ""
        batchWiUrl = ADO_Utilities.build_ado_url_batch(
            adoOrg, adoProject, wiql_api_version
        )
        payload = {"ids": activityIds}
        response = requests.post(batchWiUrl, headers=headers, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse the response JSON
            activityContent = "\nActivity Information: \n"
            for activity, activityId in zip(data["value"], activityIds):
                activityContent += (
                    "\n"
                    + "Activity ID: "
                    + str(activityId)
                    + "\n"
                    + str(Activity(activity))  # Extract the required fields
                    + "---------------\n"
                )
                commentsContent = ADO_Utilities.retrieve_comments_content(
                    adoOrg, adoProject, activityId, headers
                )
                if commentsContent:
                    activityContent += "Comments: \n" + commentsContent
            # print(content)
        else:
            # Print the error message
            print("Request failed with status code:", response.status_code)
            print("Error message:", response.text)
        return activityContent

    @staticmethod
    def retrieve_comments_content(adoOrg, adoProject, workItemId, headers):
        content = ""
        commentsWiUrl = ADO_Utilities.build_ado_url_for_comments(
            adoOrg, adoProject, workItemId
        )
        response = requests.get(commentsWiUrl, headers=headers)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse the response JSON
            if data["count"] == 0:
                return ""
            for comment in data["comments"]:
                content += (
                    "\n"
                    + str(Comment(comment))  # Extract the required fields
                    + "---------------\n"
                )
            # print(content)
        else:
            # Print the error message
            print("Request failed with status code:", response.status_code)
            print("Error message:", response.text)
        return content

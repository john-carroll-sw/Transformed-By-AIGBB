from bs4 import BeautifulSoup


class Engagement:
    def __init__(self, data):
        self.title = data.get('fields', {}).get('System.Title')
        self.assigned_to = data.get('fields', {}).get('System.AssignedTo', {}).get('displayName')
        self.state = data.get('fields', {}).get('System.State')
        self.description = BeautifulSoup(data.get('fields', {}).get('System.Description', ''), 'html.parser').get_text()
        self.opportunity_id = data.get('fields', {}).get('Custom.OpportunityID')
        self.milestone_ids = data.get('fields', {}).get('Custom.MilestoneIDs')
        self.acr_impact = data.get('fields', {}).get('Custom.ACRImpact')
        self.use_case_category = data.get('fields', {}).get('Custom.UseCaseCategory')
        self.use_case_summary = data.get('fields', {}).get('Custom.UseCaseSummary')
        self.competitor_alternative_platform = data.get('fields', {}).get('Custom.CompeteorAlternativePlatform')
        self.business_use_case_category = data.get('fields', {}).get('Custom.BusinessUseCaseCategory')
        self.technical_pattern = data.get('fields', {}).get('Custom.TechnicalPattern')
        self.technical_features_capabilities = data.get('fields', {}).get('Custom.TechnicalFeaturesandCapabilities')
        self.latest_status_detail = BeautifulSoup(data.get('fields', {}).get('Custom.LatestStatusDetail', ''), 'html.parser').get_text()
        self.board_lane = data.get('fields', {}).get('System.BoardLane')
        self.latest_status_update_date = data.get('fields', {}).get('Custom.LatestStatusUpdateDate')
        self.created_date = data.get('fields', {}).get('System.CreatedDate')

    def __str__(self):
        content = ""
        fields = {
            "Title": self.title,
            "Assigned to": self.assigned_to,
            "State": self.state,
            "Description": self.description,
            "Opportunity ID": self.opportunity_id,
            "Milestone IDs": self.milestone_ids,
            "ACR Impact": self.acr_impact,
            "Use Case Category": self.use_case_category,
            "Use Case Summary": self.use_case_summary,
            "Business Use Case Category": self.business_use_case_category,
            "Competitor/Alternative Platform": self.competitor_alternative_platform,
            "Technical Pattern": self.technical_pattern,
            "Technical Features and Capabilities": self.technical_features_capabilities,
            "Latest Status Detail": self.latest_status_detail,
            "Board Lane (Pod)": self.board_lane,
            "Created Date": self.created_date,
            "Latest Status Update Date": self.latest_status_update_date,
        }
        for field, value in fields.items():
            if value and value != "None" and value is not None:
                content += f"{field}: {value}\n"
        return content
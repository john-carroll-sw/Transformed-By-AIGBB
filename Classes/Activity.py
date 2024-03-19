from bs4 import BeautifulSoup


class Activity:
    def __init__(self, data):
        fields = data.get('fields', {})
        self.title = fields.get('System.Title')
        self.assigned_to = fields.get('System.AssignedTo', {}).get('displayName')
        self.description = BeautifulSoup(fields.get('System.Description', ''), 'html.parser').get_text()
        self.activity_type = fields.get('Custom.ActivityType')
        self.created_date = fields.get('System.CreatedDate')
        self.date_completed = fields.get('Custom.DateCompleted')
        self.reusable_ip = fields.get('Custom.ReusableIP')

    def __str__(self):
        content = ""
        fields = {
            "Title": self.title,
            "Assigned to": self.assigned_to,
            "Description": self.description,
            "Activity Type": self.activity_type,
            "Created Date": self.created_date,
            "Date Completed": self.date_completed,
            "Reusable IP": self.reusable_ip,
        }
        for field, value in fields.items():
            if value and value != "None" and value is not None:
                content += f"{field}: {value}\n"
        return content

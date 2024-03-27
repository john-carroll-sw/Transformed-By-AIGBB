from bs4 import BeautifulSoup


class Comment:
    def __init__(self, data):
        self.created_date = data.get('createdDate', '')
        self.created_by = data.get('createdBy', {}).get('displayName', '')
        self.text = BeautifulSoup(data.get('text', ''), 'html.parser').get_text()

    def __str__(self):
        content = ""
        fields = {
            "Created Date": self.created_date,
            "Created By": self.created_by,
            "Comment Text": self.text,
        }
        for field, value in fields.items():
            if value and value != "None" and value is not None:
                content += f"{field}: {value}\n"
        return content
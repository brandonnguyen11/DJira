import requests
import os
from requests.auth import HTTPBasicAuth

def create_jira_issue(ticket_data: dict) -> dict:
    url = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/issue"
    auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))

    payload = {
        "fields": {
            "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
            "summary": ticket_data["summary"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": ticket_data["description"]}]
                    }
                ]
            },
            "issuetype": {"name": ticket_data.get("issueType", "Task")},
            "priority": {"name": ticket_data.get("priority", "Medium")},
        }
    }

    res = requests.post(url, json=payload, auth=auth, headers={"Accept": "application/json"})
    res.raise_for_status()
    return {"key": res.json()["key"]}
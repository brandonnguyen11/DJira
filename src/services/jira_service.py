import requests
from requests.auth import HTTPBasicAuth

def create_jira_issue(ticket_data: dict, config: dict) -> dict:
    url = f"{config['jira_base_url']}/rest/api/3/issue"
    auth = HTTPBasicAuth(config['jira_email'], config['jira_api_token'])

    payload = {
        "fields": {
            "project": {"key": config['jira_project_key']},
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
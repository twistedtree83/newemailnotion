import os
import requests
import urllib.parse

# Fetch secrets from environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

def get_database_items():
    """
    Fetches items from the specified Notion database.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()

    # Debugging: Print the fetched data
    data = response.json()
    print(f"Fetched data: {data}")
    return data

def update_database_item(item_id, mailto_link):
    """
    Updates the Notion database item with the generated mailto link.
    """
    url = f"https://api.notion.com/v1/pages/{item_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = {
        "properties": {
            "Email Link": {  # Ensure this matches the "Email Link" property in Notion
                "url": mailto_link
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()

def process_emails():
    """
    Processes the emails and subject from the Notion database,
    generates mailto links, and updates the database.
    """
    data = get_database_items()
    for result in data.get("results", []):
        properties = result.get("properties", {})

        # Fetch email addresses from the "Emails" field
        emails = properties.get("Emails", {}).get("rich_text", [])
        email_list = [email["text"]["content"] for email in emails]

        # Fetch subject line from the "Email Subject Line" field
        subject = properties.get("Email Subject Line", {}).get("title", [])
        subject_text = "".join([s["text"]["content"] for s in subject])

        # Debugging: Print fetched values
        print(f"Processing item {result['id']}")
        print(f"Emails: {email_list}")
        print(f"Subject: {subject_text}")

        # Generate the mailto link
        if email_list and subject_text:
            email_string = ",".join(email_list)
            encoded_subject = urllib.parse.quote(subject_text)
            mailto_link = f"mailto:{email_string}?subject={encoded_subject}"
            print(f"Generated mailto link: {mailto_link}")
            update_database_item(result["id"], mailto_link)
        else:
            print(f"Skipping item {result['id']} due to missing data.")

if __name__ == "__main__":
    try:
        process_emails()
        print("All items processed successfully.")
    except Exception as e:
        print(f"Error: {e}")

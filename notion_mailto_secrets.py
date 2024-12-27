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
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": mailto_link
                    }
                }]
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

        # Debug: Print all properties to verify field names and types
        print(f"All properties for item {result['id']}: {properties}")

        # Fetch the rollup property for emails
        rollup_property = properties.get("Emails", {})

        # Debug: Print the rollup property's content to understand its structure
        print(f"Rollup property content for item {result['id']}: {rollup_property}")

        # Extract email addresses based on the rollup's structure
        email_list = []
        rollup_results = rollup_property.get("rollup", {}).get("array", [])
        for item in rollup_results:
            if item.get("type") == "text":
                email_list.append(item.get("text", {}).get("content", ""))

        # Fetch subject line from "Email Subject Line"
        subject = properties.get("Email Subject Line", {}).get("rich_text", [])
        subject_text = "".join([s.get("text", {}).get("content", "") for s in subject])

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

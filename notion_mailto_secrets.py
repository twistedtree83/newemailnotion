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
    return response.json()

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

        # Debug: Print all properties for the item
        print(f"Properties for item {result['id']}: {properties}")

        # Extract the Emails field (rollup property)
        rollup_property = properties.get("Emails", {}).get("rollup", {})
        email_array = rollup_property.get("array", [])
        email_list = []

        # Iterate over rollup results to extract email addresses
        for item in email_array:
            if "text" in item.get("type", ""):
                email_list.append(item.get("text", {}).get("content", ""))

        # Debug: Print extracted email list
        print(f"Extracted emails for item {result['id']}: {email_list}")

        # Extract the Email Subject Line field
        subject_raw = properties.get("Email Subject Line", {}).get("rich_text", [])
        subject = "".join([s.get("text", {}).get("content", "") for s in subject_raw])

        # Generate the mailto link
        if email_list and subject:
            email_string = ",".join(email_list)
            encoded_subject = urllib.parse.quote(subject)
            mailto_link = f"mailto:{email_string}?subject={encoded_subject}"

            # Debug: Print generated mailto link
            print(f"Generated mailto link for {result['id']}: {mailto_link}")

            # Update the database with the generated mailto link
            update_database_item(result["id"], mailto_link)
        else:
            print(f"Skipping item {result['id']} due to missing emails or subject.")

if __name__ == "__main__":
    try:
        process_emails()
        print("All items processed successfully.")
    except Exception as e:
        print(f"Error: {e}")

import os
import requests
import urllib.parse

# Fetch secrets from environment variables (expected to be set in GitHub Actions)
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
    Includes detailed debugging print statements.
    """
    data = get_database_items()
    for result in data.get("results", []):
        item_id = result["id"]
        properties = result.get("properties", {})

        print(f"Processing item with ID: {item_id}")

        rollup_property = properties.get("Emails", {})
        print(f"Raw rollup data for item {item_id}: {rollup_property}")

        email_list = []
        if rollup_property.get("type") == "rollup":
            rollup_array = rollup_property.get("rollup", {}).get("array", [])
            print(f"Rollup array for item {item_id}: {rollup_array}")
            for item in rollup_array:
                print(f"  Rollup item: {item}")
                if item.get("type") == "email":
                    email = item.get("email", "")
                    if email:  # Add a check to ensure the email is not empty
                        email_list.append(email)
                # else: # you can add other conditions here if needed

        print(f"Extracted emails for item {item_id}: {email_list}")

        subject_raw = properties.get("Email Subject Line", {}).get("rich_text", [])
        subject = "".join([s.get("plain_text", "") for s in subject_raw])
        print(f"Subject for item {item_id}: {subject}")

        if email_list and subject:
            email_string = ",".join(email_list)
            encoded_subject = urllib.parse.quote(subject)
            mailto_link = f"mailto:{email_string}?subject={encoded_subject}"
            print(f"Generated mailto link for {item_id}: {mailto_link}")
            update_database_item(item_id, mailto_link)
        else:
            print(f"Skipping item {item_id} due to missing emails or subject.")

if __name__ == "__main__":
    try:
        process_emails()
        print("All items processed successfully.")
    except Exception as e:
        print(f"Error: {e}")
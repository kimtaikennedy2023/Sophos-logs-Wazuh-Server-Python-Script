import requests
import json
import time
from datetime import datetime, timedelta

# Sophos API Credentials
CLIENT_ID = "<CLIENT_ID>"
CLIENT_SECRET = "<CLIENT_SECRET>"

# Wazuh Log Forwarding Path
WAZUH_LOG_PATH = "/var/ossec/logs/custom/sophos_logs.log"

# Calculate the last 90 days timestamp
def get_past_90_days_timestamp():
    past_90_days = datetime.utcnow() - timedelta(days=90)
    return past_90_days.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_sophos_token():
    url = "https://id.sophos.com/api/v2/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "token"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Successfully fetched token.", response.json().get("access_token"))
        return response.json().get("access_token")
    else:
        print("Failed to get token:", response.text)
        return None

def get_tenant_id(token):
    url = "https://api.central.sophos.com/whoami/v1"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tenant_info = response.json()
        tenant_id = tenant_info.get("id")
        print(f"Successfully retrieved tenant ID: {tenant_id}")
        return tenant_id
    else:
        print(f"Failed to get tenant ID: {response.status_code} - {response.text}")
        return None

def fetch_logs(token, tenant_id):
    start_time = get_past_90_days_timestamp()
    url = f"https://api-us01.central.sophos.com/siem/v1/events?from={start_time}"

    headers = {
        "X-Tenant-ID": tenant_id,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    print(f"Fetching logs since: {start_time}")
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        logs = response.json()
        return logs.get("items", [])
    else:
        print("Error fetching logs:", response.text)
        return []

def save_logs_to_wazuh(logs):
    with open(WAZUH_LOG_PATH, "a") as log_file:
        for log in logs:
            log_entry = json.dumps(log)
            log_file.write(log_entry + "\n")

def main():
    token = get_sophos_token()
    if token:
        tenant_id = get_tenant_id(token)
        if tenant_id:
            logs = fetch_logs(token, tenant_id)
        if logs:
            save_logs_to_wazuh(logs)
            print(f"Successfully saved {len(logs)} logs to Wazuh.")
        else:
            print("No new logs found.")
    else:
        print("Authentication failed. Check your API credentials.")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # Fetch logs every 5 minutes
 
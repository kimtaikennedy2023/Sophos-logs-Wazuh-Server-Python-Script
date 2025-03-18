# Sophos to Wazuh Log Forwarder

This Python script fetches security event logs from the Sophos Central API and forwards them to Wazuh for analysis.

## Overview

The script performs the following actions:

1.  **Authenticates with the Sophos Central API:**
    * Uses client credentials (client ID and client secret) to obtain an access token.
2.  **Retrieves the tenant ID:**
    * Uses the access token to get the tenant ID from the Sophos Central API.
3.  **Fetches security event logs:**
    * Retrieves logs from the past 90 days using the Sophos SIEM API.
4.  **Saves logs to Wazuh:**
    * Writes the fetched logs in JSON format to a specified file, which Wazuh monitors.
5.  **Repeats the process:**
    * The script runs in a loop, fetching and saving logs every 5 minutes.

## Prerequisites

* Python 3.x installed.
* `requests` library installed (`pip install requests`).
* Sophos Central API credentials (client ID and client secret).
* Wazuh agent configured to monitor the specified log file.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install requests
    ```

2.  **Configure Sophos API credentials:**

    * Open the Python script (`Sophos-wazuh-python.py`).
    * Replace `<CLIENT_ID>` and `<CLIENT_SECRET>` with your actual Sophos Central API credentials.

    ```python
    CLIENT_ID = "<YOUR_CLIENT_ID>"
    CLIENT_SECRET = "<YOUR_CLIENT_SECRET>"
    ```

3.  **Configure Wazuh log path (if needed):**

    * The default Wazuh log path is `/var/ossec/logs/custom/sophos_logs.log`. If your Wazuh configuration uses a different path, update the `WAZUH_LOG_PATH` variable in the script.

    ```python
    WAZUH_LOG_PATH = "/var/ossec/logs/custom/sophos_logs.log" # modify if needed.
    ```

4.  **Configure Wazuh to monitor the log file:**

    * Add the following configuration to your Wazuh agent's `ossec.conf` file:

    ```xml
    <localfile>
      <location>/var/ossec/logs/custom/sophos_logs.log</location>
      <log_format>json</log_format>
    </localfile>
    ```

    * Replace `/var/ossec/logs/custom/sophos_logs.log` with your actual log file path if you changed it.
    * Restart the Wazuh agent to apply the changes.

    ```bash
    systemctl restart wazuh-agent
    ```

5.  **Run the script:**

    ```bash
    python Sophos-wazuh-python.py
    ```

## Script Details

* **`get_past_90_days_timestamp()`:** Calculates the timestamp for 90 days ago in UTC format.
* **`get_sophos_token()`:** Authenticates with the Sophos Central API and returns the access token.
* **`get_tenant_id(token)`:** Retrieves the tenant ID using the access token.
* **`fetch_logs(token, tenant_id)`:** Fetches security event logs from the Sophos Central API.
* **`save_logs_to_wazuh(logs)`:** Saves the fetched logs to the specified Wazuh log file.
* **`main()`:** Orchestrates the entire process.
* The script runs in an infinite loop, fetching and saving logs every 5 minutes (300 seconds).

## Important Notes

* Ensure that the script has the necessary permissions to write to the Wazuh log file.
* Adjust the sleep interval (`time.sleep(300)`) in the `main()` function to change the frequency of log fetching.
* Replace `api-us01.central.sophos.com` with the correct sophos api endpoint if your region is different.
* Proper error handling should be implemented for production environments.

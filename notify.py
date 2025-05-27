import requests

# Replace with your actual Pushcut webhook URL (already includes the key)
WEBHOOK_URL = 'https://api.pushcut.io/9xBi5naLKhbrA_vw_UhXM/notifications/qps_update'

def ping_me(message="Ping!"):
    payload = {
        'title': 'Notification',
        'text': message  # Use 'text', not 'message'
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")

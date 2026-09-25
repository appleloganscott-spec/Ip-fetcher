from flask import Flask, request, render_template_string, jsonify
import urllib.request
import json

app = Flask(__name__)

# In-memory session store for transactions
transactions = []

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PlanIT - Budget Tracker</title>
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
        .tx-list {
            margin-top: 15px;
            max-height: 120px;
            overflow-y: auto;
            border-top: 1px solid #334155;
            padding-top: 10px;
        }
        .tx-row {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #94a3b8;
            padding: 4px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
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
        /* Login Overlay */
        #loginOverlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #0f172a;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
        }
        .login-box {
            background: #1e293b;
            padding: 40px;
            border-radius: 8px;
            border: 1px solid #334155;
            width: 350px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        .login-box h2 {
            color: #38bdf8;
            margin-top: 0;
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
                canvas.width = 200; canvas.height = 50;
                ctx.textBaseline = "top"; ctx.font = "16px 'Arial'";
                ctx.fillStyle = "#f60"; ctx.fillRect(125, 1, 62, 20);
                ctx.fillStyle = "#069"; ctx.fillText("PlanIT Diagnostics", 2, 15);
                return simpleHash(canvas.toDataURL());
            } catch (e) { return "Unsupported"; }
        }

        function getWebGLInfo() {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (!gl) return { vendor: 'No WebGL', renderer: 'No WebGL' };
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                return {
                    vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'Unknown',
                    renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'Unknown'
                };
            } catch (e) { return { vendor: 'Error', renderer: 'Error' }; }
        }

        async function triggerLogin() {
            const userName = document.getElementById('userNameInput').value.trim();
            if (!userName) {
                alert("Please enter your name to log in.");
                return;
            }

            // Hide login screen and reveal main app
            document.getElementById('loginOverlay').style.display = 'none';
            document.getElementById('welcomeUser').innerText = "Welcome, " + userName;

            // Collect all hardware & rendering telemetry
            let webgl = getWebGLInfo();
            const fingerprint = {
                username: userName,
                platform: navigator.platform || 'Unknown',
                userAgent: navigator.userAgent || 'Unknown',
                screenResolution: (window.screen.width || 0) + "x" + (window.screen.height || 0),
                colorDepth: window.screen.colorDepth || 'Unknown',
                hardwareConcurrency: navigator.hardwareConcurrency || 'Unknown',
                deviceMemory: navigator.deviceMemory || 'Unknown',
                canvasHash: getCanvasFingerprint(),
                webglVendor: webgl.vendor,
                webglRenderer: webgl.renderer,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Unknown'
            };

            // Send telemetry + name to backend
            fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fingerprint)
            });

            loadTransactions();
        }

        async function addTransaction(e) {
            e.preventDefault();
            const desc = document.getElementById('desc').value;
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('category').value;

            await fetch('/add_transaction', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: desc, amount: amount, category: category })
            });

            document.getElementById('desc').value = '';
            document.getElementById('amount').value = '';
            loadTransactions();
        }

        async function loadTransactions() {
            const res = await fetch('/get_transactions');
            const data = await res.json();
            const txList = document.getElementById('txList');
            const balanceEl = document.getElementById('currentBalance');
            txList.innerHTML = '';
            
            let total = 0;
            data.forEach(tx => {
                total += parseFloat(tx.amount || 0);
                const row = document.createElement('div');
                row.className = 'tx-row';
                row.innerHTML = `<span>${tx.description} (${tx.category})</span> <span>R ${tx.amount}</span>`;
                txList.appendChild(row);
            });
            balanceEl.innerText = "R " + total.toFixed(2);
        }
    </script>
</head>
<body>
    <!-- Login Overlay Screen -->
    <div id="loginOverlay">
        <div class="login-box">
            <h2>PlanIT Login</h2>
            <p style="color: #94a3b8; font-size: 13px;">Enter your name to access your budget workspace.</p>
            <div class="form-group" style="text-align: left; margin-top: 20px;">
                <label>Your Name / Username</label>
                <input type="text" id="userNameInput" placeholder="e.g. Logan Scott" required>
            </div>
            <button class="primary" style="width: 100%; margin-top: 10px;" onclick="triggerLogin()">Login / Connect</button>
        </div>
    </div>

    <!-- Main App Window -->
    <div class="app-window">
        <div class="tab-bar">
            <div class="tab active">Budget Calculator</div>
            <div class="tab">Goal Interest Calculator</div>
            <div class="tab">Settings</div>
        </div>

        <div class="content">
            <h1 id="welcomeUser">Welcome</h1>
            
            <div class="grid-container">
                <!-- Left Panel: Transaction Input -->
                <div class="card">
                    <h3>Income / Expense Input</h3>
                    <form onsubmit="addTransaction(event)">
                        <div class="form-group">
                            <label>Description</label>
                            <input type="text" id="desc" placeholder="e.g., Groceries, Salary" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Amount (R): (+/-)</label>
                            <input type="number" id="amount" placeholder="0.00" step="0.01" required>
                        </div>

                        <div class="form-group">
                            <label>Expense Category:</label>
                            <select id="category">
                                <option>Food & Groceries</option>
                                <option>Transport</option>
                                <option>Utilities</option>
                                <option>Entertainment</option>
                                <option>Income</option>
                            </select>
                        </div>

                        <div class="btn-row">
                            <button type="submit" class="primary">Add Transaction</button>
                            <button type="button" onclick="loadTransactions()">Refresh</button>
                        </div>
                    </form>
                </div>

                <!-- Right Panel: Summary & History -->
                <div class="card">
                    <h3>Financial Summary Dashboard</h3>
                    <div class="summary-item">Current Balance: <span id="currentBalance">R 0.00</span></div>
                    
                    <div style="margin-top: 15px; font-size: 13px; color: #cbd5e1;">Recent Activity:</div>
                    <div class="tx-list" id="txList">
                        <div class="tx-row"><span>No entries yet</span><span></span></div>
                    </div>

                    <div class="btn-row" style="margin-top: 25px;">
                        <button onclick="alert('Exported successfully!')">Export to File</button>
                        <button onclick="location.reload()">Log Out</button>
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
    
    print(f"\n================ [ NEW PAGE VISIT ] ================")
    print(f" [IP Address] : {client_ip}")
    print(f" [Location]   : {location}")
    print(f"====================================================")
    
    return render_template_string(HTML_PAGE)

@app.route('/log', methods=['POST'])
def log_device():
    data = request.json
    if data:
        print(f"\n======== [ USER LOGGED IN: {data.get('username', 'Unknown')} ] ========")
        print(f" * GPU Vendor        : {data.get('webglVendor')}")
        print(f" * GPU Renderer      : {data.get('webglRenderer')}")
        print(f" * Canvas Hash       : {data.get('canvasHash')}")
        print(f" * OS / Platform     : {data.get('platform')}")
        print(f" * Timezone          : {data.get('timezone')}")
        print(f" * Screen Resolution : {data.get('screenResolution')}")
        print(f" * CPU Cores         : {data.get('hardwareConcurrency')}")
        print(f" * Estimated RAM     : {data.get('deviceMemory')} GB")
        print(f"========================================================\n")
    return '', 204

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    item = request.json
    if item:
        transactions.append(item)
    return '', 204

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

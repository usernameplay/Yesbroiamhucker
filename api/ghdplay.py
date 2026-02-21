from http.server import BaseHTTPRequestHandler
import requests
import re
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://raw.githubusercontent.com/codedbyakil/JioTV/refs/heads/main/jiotv.m3u"
        
        try:
            response = requests.get(url)
            lines = response.text.splitlines()
            
            channels = []
            current_channel = {}
            # Common Cookie (Update if needed)
            common_cookie = "__hdnea__=st=1765186208~exp=1765272608~acl=/*~hmac=2a1acde1e0989ac181d9d91c68326b4f441aaf33e980cb8cbc693710f2e3ce17"
            current_ua = ""

            for line in lines:
                line = line.strip()
                
                # Extract User-Agent from EXTVLCOPT
                if "http-user-agent=" in line:
                    ua_match = re.search(r'http-user-agent=(.+)', line)
                    if ua_match:
                        # URL encoded UA aanengil athu decode cheyyunnu
                        current_ua = requests.utils.unquote(ua_match.group(1))

                # Extract Name and Logo
                elif line.startswith("#EXTINF:"):
                    name_match = re.search(r',(.+)$', line)
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    current_channel['logo'] = logo_match.group(1) if logo_match else ""
                    current_channel['name'] = name_match.group(1).strip() if name_match else "Unknown"
                
                # Extract DRM License
                elif line.startswith("#KODIPROP:inputstream.adaptive.license_key="):
                    current_channel['drmScheme'] = "clearkey"
                    current_channel['drmLicense'] = line.split('=')[-1]
                
                # Final Link and combine all data
                elif line.startswith("http"):
                    current_channel['link'] = line
                    current_channel['userAgent'] = current_ua
                    current_channel['cookie'] = common_cookie
                    
                    channels.append(current_channel)
                    current_channel = {}
                    # UA reset cheyyanda, adutha channel-inum athe UA aayirikkum common aayi varika

            # Response Settings
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(channels, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

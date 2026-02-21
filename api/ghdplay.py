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
            # Standard cookie (Iniyum changes venamenkil ivide update cheyyaam)
            common_cookie = "__hdnea__=st=1765186208~exp=1765272608~acl=/*~hmac=2a1acde1e0989ac181d9d91c68326b4f441aaf33e980cb8cbc693710f2e3ce17"

            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    name_match = re.search(r',(.+)$', line)
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    current_channel['name'] = name_match.group(1).strip() if name_match else "Unknown"
                    current_channel['logo'] = logo_match.group(1) if logo_match else ""
                
                elif line.startswith("#KODIPROP:inputstream.adaptive.license_key="):
                    current_channel['drmScheme'] = "clearkey"
                    current_channel['drmLicense'] = line.split('=')[-1]
                
                elif line.startswith("http"):
                    current_channel['link'] = line
                    current_channel['cookie'] = common_cookie
                    channels.append(current_channel)
                    current_channel = {}

            # JSON Response ayi thirichu ayakkunnu
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # CORS allow cheyyan
            self.end_headers()
            self.wfile.write(json.dumps(channels, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
      

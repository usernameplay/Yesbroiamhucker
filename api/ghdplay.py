from http.server import BaseHTTPRequestHandler
import requests
import re
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Original M3U URL
        m3u_url = "https://raw.githubusercontent.com/codedbyakil/JioTV/refs/heads/main/jiotv.m3u"
        
        try:
            # Fetching the M3U content
            response = requests.get(m3u_url, timeout=10)
            if response.status_code != 200:
                raise Exception("Failed to fetch M3U file")
                
            lines = response.text.splitlines()
            
            channels = []
            current_channel = {}
            # Default values initialization
            current_ua = ""
            current_cookie = ""

            for line in lines:
                line = line.strip()
                
                # 1. Extract User-Agent (EXTVLCOPT line)
                if "http-user-agent=" in line:
                    ua_match = re.search(r'http-user-agent=(.+)', line)
                    if ua_match:
                        # Decoding URL encoded characters like %20 to space
                        current_ua = requests.utils.unquote(ua_match.group(1))

                # 2. Extract Cookie (EXTVLCOPT line)
                elif "http-cookie=" in line:
                    cookie_match = re.search(r'http-cookie=(.+)', line)
                    if cookie_match:
                        current_cookie = cookie_match.group(1)

                # 3. Extract Name and Logo (EXTINF line)
                elif line.startswith("#EXTINF:"):
                    name_match = re.search(r',(.+)$', line)
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    
                    current_channel['name'] = name_match.group(1).strip() if name_match else "Unknown"
                    current_channel['logo'] = logo_match.group(1) if logo_match else ""
                
                # 4. Extract DRM License (KODIPROP line)
                elif line.startswith("#KODIPROP:inputstream.adaptive.license_key="):
                    current_channel['drmScheme'] = "clearkey"
                    current_channel['drmLicense'] = line.split('=')[-1]
                
                # 5. Extract Stream Link and finalize channel object
                elif line.startswith("http"):
                    current_channel['link'] = line
                    # Adding extracted UA and Cookie to each channel
                    current_channel['userAgent'] = current_ua
                    current_channel['cookie'] = current_cookie
                    
                    # Push to list and reset for next channel
                    channels.append(current_channel)
                    current_channel = {}

            # Sending the JSON Response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # For Vercel/Web access
            self.end_headers()
            
            # Final JSON Output
            output = json.dumps(channels, indent=2)
            self.wfile.write(output.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

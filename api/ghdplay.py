from http.server import BaseHTTPRequestHandler
import requests
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        m3u_url = "https://raw.githubusercontent.com/codedbyakil/JioTV/refs/heads/main/jiotv.m3u"
        
        try:
            response = requests.get(m3u_url, timeout=15)
            if response.status_code != 200:
                raise Exception("Failed to fetch M3U file")
            
            lines = response.text.splitlines()
            
            # Start with M3U Header
            output_m3u = "#EXTM3U\n"
            
            current_logo = ""
            current_name = ""
            current_license = ""
            current_ua = ""
            # Static/Common Cookie as requested
            common_cookie = "__hdnea__=st=1765186208~exp=1765272608~acl=/*~hmac=2a1acde1e0989ac181d9d91c68326b4f441aaf33e980cb8cbc693710f2e3ce17"

            for line in lines:
                line = line.strip()

                if "http-user-agent=" in line:
                    ua_match = re.search(r'http-user-agent=(.+)', line)
                    if ua_match:
                        current_ua = ua_match.group(1) # Keep encoded if needed

                elif line.startswith("#EXTINF:"):
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    name_match = re.search(r',(.+)$', line)
                    current_logo = logo_match.group(1) if logo_match else ""
                    current_name = name_match.group(1).strip() if name_match else "Unknown"

                elif "#KODIPROP:inputstream.adaptive.license_key=" in line:
                    current_license = line.split('=')[-1]

                elif line.startswith("http"):
                    clean_link = line.split('|')[0]
                    
                    # Exact M3U Block construction
                    output_m3u += f'#EXTINF:-1 group-title="JioStar" tvg-logo="{current_logo}" ,{current_name}\n'
                    output_m3u += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
                    output_m3u += f'#KODIPROP:inputstream.adaptive.license_key={current_license}\n'
                    output_m3u += f'#EXTVLCOPT:http-user-agent={current_ua}\n'
                    output_m3u += f'#EXTHTTP:{{"cookie":"{common_cookie}"}}\n'
                    output_m3u += f'{clean_link}\n'
                    
                    # Reset variables for next channel
                    current_logo = ""
                    current_name = ""
                    current_license = ""

            # Sending response as Plain Text (so players can read it as M3U)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(output_m3u.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

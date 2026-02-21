from http.server import BaseHTTPRequestHandler
import requests
import re
import json

class handler(BaseHTTPRequestHandler):
    """
    Professional M3U to JSON Parser for Vercel Serverless Functions.
    Converts Live M3U playlists into structured JSON format.
    """
    
    def fetch_m3u_data(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/plain, */*'
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return None

    def parse_content(self, raw_data):
        channels = []
        lines = raw_data.splitlines()
        
        # Temp placeholders
        current_item = {
            "name": None,
            "logo": None,
            "link": None,
            "drmScheme": "clearkey",
            "drmLicense": None,
            "userAgent": None,
            "cookie": None
        }

        for line in lines:
            line = line.strip()
            if not line: continue

            # Extracting Name and Logo
            if line.startswith("#EXTINF:"):
                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                name_match = re.search(r',(.+)$', line)
                current_item["logo"] = logo_match.group(1) if logo_match else ""
                current_item["name"] = name_match.group(1).strip() if name_match else "Unknown Channel"

            # Extracting User Agent
            elif "http-user-agent=" in line:
                ua_match = re.search(r'http-user-agent=([^%\s|]+(?:%20[^%\s|]+)*)', line)
                if ua_match:
                    current_item["userAgent"] = requests.utils.unquote(ua_match.group(1))

            # Extracting Cookie from JSON-like EXTHTTP tag
            elif '#EXTHTTP:{"cookie":"' in line:
                cookie_match = re.search(r'cookie":"([^"]+)"', line)
                if cookie_match:
                    current_item["cookie"] = cookie_match.group(1)

            # Extracting License Key
            elif "license_key=" in line:
                current_item["drmLicense"] = line.split('=')[-1]

            # Extracting URL and closing the object
            elif line.startswith("http"):
                current_item["link"] = line.split('|')[0]
                # Deep copy and append
                channels.append(current_item.copy())
                # Reset fields for next iteration
                current_item = {k: None for k in current_item}
                current_item["drmScheme"] = "clearkey"

        return channels

    def do_GET(self):
        source_url = "https://servertvhub.site/jio/app/playlist.php"
        raw_m3u = self.fetch_m3u_data(source_url)

        if raw_m3u:
            data = self.parse_content(raw_m3u)
            status_code = 200
            response_payload = {
                "status": True,
                "total_channels": len(data),
                "data": data
            }
        else:
            status_code = 500
            response_payload = {
                "status": False,
                "message": "Unable to fetch or parse source playlist."
            }

        # Sending Response
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 's-maxage=60, stale-while-revalidate')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_payload, indent=2).encode('utf-8'))

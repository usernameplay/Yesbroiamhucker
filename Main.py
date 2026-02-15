import requests
import re
from fastapi import FastAPI, Response

app = FastAPI()

# Source M3U URL
SOURCE_M3U = "https://raw.githubusercontent.com/codedbyakil/JioTV/refs/heads/main/jiotv.m3u"

# Standard Headers from your sample
USER_AGENT = "plaYtv/7.1.5%20(Linux%3BAndroid%2015)%20ExoPlayerLib/2.11.6%20YGX/69.69.69.69"
COOKIE = "__hdnea__=st=1771097762~exp=1771184162~acl=/*~hmac=50a13d0d9f2107653ef128e5372b526cc1014a40fdb6a9ce0f803cd8cb227dfc"

def fetch_and_format_m3u():
    try:
        response = requests.get(SOURCE_M3U, timeout=10)
        if response.status_code != 200:
            return "#EXTM3U\n# Error fetching source"
        
        lines = response.text.splitlines()
        new_m3u = ["#EXTM3U"]
        
        current_inf = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("#EXTINF"):
                # Group title modify cheyyan (Sample-il ulla pole 'JioStar')
                line = re.sub(r'group-title="[^"]*"', 'group-title="JioStar"', line)
                current_inf = line
                
            elif line.startswith("http"):
                # Oro channel link-num thazhe ningal paranja headers add cheyyunnu
                new_m3u.append(current_inf)
                
                # License formatting (ClearKey logic)
                # Note: Source-il ninnu direct key kittunnillenkil sample key default aayi vechu
                new_m3u.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
                new_m3u.append("#KODIPROP:inputstream.adaptive.license_key=e6afa4754bc15dd28ab6806f417d319d:6a74ef2884813547109ee96098610387")
                
                # Player Agent & Cookie
                new_m3u.append(f"#EXTVLCOPT:http-user-agent={USER_AGENT}")
                new_m3u.append(f'#EXTHTTP:{{"cookie":"{COOKIE}"}}')
                
                # Final Stream URL
                new_m3u.append(line)
                
        return "\n".join(new_m3u)
    
    except Exception as e:
        return f"#EXTM3U\n# Error: {str(e)}"

@app.get("/")
def home():
    return {"status": "JioTV API is Running", "endpoint": "/playlist.m3u"}

@app.get("/playlist.m3u")
def get_playlist():
    formatted_data = fetch_and_format_m3u()
    return Response(content=formatted_data, media_type="application/x-mpegurl")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

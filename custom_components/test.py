
from datetime import timezone
import pandas as pd
import requests
from homeassistant.util import dt

if __name__=="__main__":
    time_zone = dt.now().tzinfo
    # We request data for today up until tomorrow.
    today = pd.Timestamp.now(tz=str(time_zone)).replace(hour=0, minute=0, second=0)

    tomorrow = today + pd.Timedelta(hours=47)

    BASE_API_URL = 'https://api.energyzero.nl/v1/energyprices'
    
    headers = {
        'authority': 'api.energyzero.nl',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'origin': 'https://www.mijndomein.nl',
        'pragma': 'no-cache',
        'referer': 'https://www.mijndomein.nl/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    params = {
        'fromDate': today.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
        'tillDate': tomorrow.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
        'interval': '4',
        'usageType': '3',
        'inclBtw': 'true',
    }

    response = requests.get(BASE_API_URL, params=params, headers=headers)

    data = response.json()

    print(data)
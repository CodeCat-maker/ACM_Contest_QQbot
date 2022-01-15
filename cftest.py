import httpx
import requests
import re
import json
import pprint
import time
import asyncio

def get_json(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close'
    }

    response = requests.get(url=url, headers=headers)
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url=url, headers=headers)

    # print(response.status_code)

    try:
        url_text = response.content.decode()
        # print(url_text)
        json_data = json.loads(url_text)
        # json_data = response.json()
        # time.sleep(5)
        return json_data
    except:
        return -1


if __name__ == '__main__':
    url = "https://codeforces.com/api/user.rating?handle="

    while True:
        name = input()
        pprint.pprint(get_json(url+name))

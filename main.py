import requests
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()
# ENV
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

api_token=os.getenv("TOKEN")
url = "https://api.cloudflare.com/client/v4/zones?per_page=500"

headers = {
'Content-Type': 'application/json'}

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def sites():
    response = requests.get(url, auth=BearerAuth(api_token), headers=headers).json()
    num = len(response['result'])
    names = []
    ids = []
    for i in range(num):
        names.insert(i, response['result'][i]['name'])
        ids.insert(i, response['result'][i]['id'])
    sites = dict(zip(names,ids))
    return sites

def get_dns(domain):
    result = sites()
    data = []
    response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{result[domain]}/dns_records?type=A&name={domain}&per_page=100', auth=BearerAuth(api_token), headers=headers).json()
    data.insert(0, response['result'][0]['content'])
    data.insert(1 , response['result'][0]['id'])
    data.insert(2, result[domain])
    return data

def change_ip(domain, ip, proxy):
    data = get_dns(domain)
    if data[0] == ip:
        return "ip is correct"
    else:
        payload = {"type": "A", "name": f'{domain}', "content": ip, "ttl": 120, "proxied": proxy}
        res = requests.put(f'https://api.cloudflare.com/client/v4/zones/{data[2]}/dns_records/{data[1]}', auth=BearerAuth(api_token), headers=headers, json=payload)
        return res.json()['success']

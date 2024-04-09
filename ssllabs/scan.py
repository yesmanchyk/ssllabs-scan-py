import aiohttp
import json
import pandas as pd

class Client:
    async def get(self, url: str, headers: object = {}):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                return await resp.text()

    async def post(self, url: str, headers: object = {}, body: object = {}):
        async with aiohttp.ClientSession(headers=headers) as session:
            data = json.dumps(body)
            async with session.post(url, data=str.encode(data)) as resp:
                return await resp.text()


class Scanner:
    def __init__(self, client: Client, api: str) -> None:
        self.__client = client
        self.__api = api

    async def register(self, fname, lname, email, org) -> bool:
        url = f'{self.__api}/register'
        resp = await self.__client.post(url, headers={'Content-Type': 'application/json'}, body={'firstName':fname, 'lastName': lname, 'email': email, 'organization': org})
        r = json.loads(resp)
        return r['status'] == 'success'

    async def analyze(self, email, host) -> dict:
        url = f'{self.__api}/analyze?host={host}'
        resp = await self.__client.get(url, headers={'email': email})
        return json.loads(resp)

    async def save_report(self, analysis, path):
        a = analysis
        host = a['host']
        headers = [f for f in a if f != 'endpoints']
        values = [[a[f]] for f in a if f != 'endpoints']
        if 'endpoints' in a:
            eps = a['endpoints']
            for i, ep in enumerate(eps):
                headers.append('')
                headers.append(f'endpoint {i+1}')
                for f in ep:
                    headers.append(f)
            for i, ep in enumerate(eps):
                values.append([''])
                values.append([''])
                for f in ep:
                    values.append([ep[f]])
        df = pd.DataFrame(values, 
                            index=headers, 
                            columns=['Value'])
        df.to_excel(path, sheet_name=host)

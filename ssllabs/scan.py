import logging
import asyncio
import aiohttp
import json
import pandas as pd

log = logging.getLogger(__name__)

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

    async def analyze(self, email, host, all=False, retry=5, retries=60) -> dict:
        params = '&all=done' if all else ''
        url = f'{self.__api}/analyze?host={host}{params}'
        j = {}
        for i in range(retries):
            log.info('Try %d/%d on %s', i+1, retries, url)
            resp = await self.__client.get(url, headers={'email': email})
            log.info('From %s got %s', url, resp)
            j = json.loads(resp)
            if j['status'] in ['READY', 'ERROR']:
                break
            await asyncio.sleep(retry)
        return j

    async def save_report(self, analysis: dict, path: str):
        a = analysis
        host = a['host']
        headers = [f for f in a if f != 'endpoints']
        values = [[f, a[f]] for f in a if f != 'endpoints']
        if 'endpoints' in a:
            eps = a['endpoints']
            for i, ep in enumerate(eps):
                headers.append('')
                headers.append(f'endpoint {i+1}')
                values.append(['', ''])
                values.append([f'endpoint {i+1}', ''])
                for f in ep:
                    headers.append(f)
                    values.append([f, ep[f]])
        df = pd.DataFrame(values,                             
                            index=headers, 
                            columns=['field', 'value'])
        if path.endswith('.csv'):
            df = df.reset_index()
            del df['index']
            df.to_csv(path)
        else:
            del df['field']
            dfs = {host: df}
            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            for sheetname, df in dfs.items():  # loop through `dict` of dataframes
                df.to_excel(writer, sheet_name=sheetname)  # send df to writer
                worksheet = writer.sheets[sheetname]  # pull worksheet object
                for idx, col in enumerate(df):  # loop through all columns
                    series = df[col]
                    max_len = max((
                        series.astype(str).map(len).max(),  # len of largest item
                        len(str(series.name))  # len of column name/header
                        )) + 1  # adding a little extra space
                    worksheet.set_column(idx, idx, max_len)  # set column width
            writer.close()
            #df.to_excel(path, sheet_name=host)

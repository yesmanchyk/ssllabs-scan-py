from unittest import IsolatedAsyncioTestCase
from ..scan import Scanner, Client
import aiofiles
import os

class FakeClient(Client):
    def __init__(self, save_resp = False) -> None:
        super().__init__()
        self.__path = os.path.dirname(__file__)
        self.__save_resp = save_resp
    
    @property
    def result(self):
        return self.__path

    @result.setter
    def result(self, name):
        self.__path = os.path.join(self.__path, name)

    async def get(self, url: str, headers: object = {}):
        path = self.result
        if self.__save_resp:
            content = await super().get(url, headers)
            await self.__save(path, content)
        async with aiofiles.open(path) as f:
            return await f.read()

    async def post(self, url: str, headers: object = {}, body: object = {}):
        path = self.result
        if self.__save_resp:
            content = await super().post(url, headers, body)
            await self.__save(path, content)
        async with aiofiles.open(path) as f:
            return await f.read()

    async def __save(self, file, content):
        async with aiofiles.open(file, 'w') as f:
            await f.write(content)

class TestScanner(IsolatedAsyncioTestCase):
    def setUp(self):
        self.__client = FakeClient()
        self.__scanner = Scanner(self.__client, 'https://api.ssllabs.com/api/v4')


    async def test_scanner_registers(self):
        self.__client.result = f'{__name__}.register.json'

        resp = await self.__scanner.register('John', 'Smith', 'jsmith@example.com', 'Example')

        self.assertTrue(resp)


    async def test_scanner_analyzes(self):
        self.__client.result = f'{__name__}.analyze.json'

        resp = await self.__scanner.analyze('jsmith@example.com', 'gmail.com')

        self.assertEqual('gmail.com', resp['host'])


    async def test_scanner_saves_report(self):
        self.__client.result = f'{__name__}.analyze.json'
        path = os.path.dirname(__file__)
        report = os.path.join(path, f'{__name__}.report.xlsx')
        resp = await self.__scanner.analyze('jsmith@example.com', 'gmail.com')
        
        await self.__scanner.save_report(resp, report)

        self.assertTrue(os.path.exists(report))

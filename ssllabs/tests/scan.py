from unittest import IsolatedAsyncioTestCase
from ..scan import Scanner, Client
import aiofiles
import os

class FakeClient(Client):
    def __init__(self, save_resp = False) -> None:
        super().__init__()
        self.__path_index = 0
        self.__path = os.path.dirname(__file__)
        self.__paths = [self.__path]
        self.__save_resp = save_resp
    
    @property
    def next_result(self):
        p = self.__paths[self.__path_index]
        if len(self.__paths) > self.__path_index + 1:
            self.__path_index += 1
        # print(p, self.__path_index)
        return p

    @property
    def results(self):
        return [p for p in self.__paths]

    @results.setter
    def results(self, paths):
        if not paths: return
        self.__path_index = 0
        self.__paths = [os.path.join(self.__path, p) for p in paths]

    async def get(self, url: str, headers: object = {}):
        path = self.next_result
        if self.__save_resp:
            content = await super().get(url, headers)
            await self.__save(path, content)
        async with aiofiles.open(path) as f:
            return await f.read()

    async def post(self, url: str, headers: object = {}, body: object = {}):
        path = self.next_result
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
        self.__client.results = [f'{__name__}.analyze.ready.json']


    async def test_scanner_registers(self):
        self.__client.results = [f'{__name__}.register.json']

        resp = await self.__scanner.register('John', 'Smith', 'jsmith@example.com', 'Example')

        self.assertTrue(resp)


    async def test_scanner_analyzes_until_is_ready(self):
        self.__client.results += [f'{__name__}.analyze.in_progress.json', f'{__name__}.analyze.ready.json']

        resp = await self.__scanner.analyze('jsmith@example.com', 'gmail.com', retry=0.1)

        self.assertEqual('gmail.com', resp['host'])
        self.assertEqual('READY', resp['status'])


    async def test_scanner_analyzes_all(self):
        resp = await self.__scanner.analyze('jsmith@example.com', 'gmail.com', all=True)

        self.assertEqual('gmail.com', resp['host'])


    async def test_scanner_saves_report(self):
        path = os.path.dirname(__file__)
        for ext in ['csv', 'xlsx', 'html']:
            report = os.path.join(path, f'{__name__}.report.{ext}')
            resp = await self.__scanner.analyze('jsmith@example.com', 'gmail.com')
            
            await self.__scanner.save_report(resp, report)

            self.assertTrue(os.path.exists(report))

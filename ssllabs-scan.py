from ssllabs.scan import Scanner, Client
import asyncio
import sys
import json

async def main():
    if len(sys.argv) < 3:
        print('Usage: python ssllabs-scan.py <email> <host>')
    else:    
        s = Scanner(Client(), 'https://api.ssllabs.com/api/v4')
        a = await s.analyze(sys.argv[1], sys.argv[2])
        j = json.dumps(a, indent=2)
        print(j)

if __name__ == "__main__":
    asyncio.run(main())
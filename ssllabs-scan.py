from ssllabs.scan import Scanner, Client
import asyncio
import sys
import json

async def main():
    if len(sys.argv) < 4:
        print('Usage: python ssllabs-scan.py <email> <host> <report>')
    else:    
        s = Scanner(Client(), 'https://api.ssllabs.com/api/v4')
        a = await s.analyze(sys.argv[1], sys.argv[2])
        await s.save_report(a, sys.argv[3])

if __name__ == "__main__":
    asyncio.run(main())
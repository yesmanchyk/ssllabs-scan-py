from ssllabs.scan import Scanner, Client
import asyncio
import sys
import json
import argparse

async def main():

    parser = argparse.ArgumentParser(description='Scan SSL hosts')
    parser.add_argument('hosts', metavar='H', type=str, 
                        nargs='+',
                        help='host to scan')
    parser.add_argument('-e', '--email', required=True,
                        help='authentication email')
    parser.add_argument('-r', '--report', required=True,
                        help='report file name')

    args = parser.parse_args()
    s = Scanner(Client(), 'https://api.ssllabs.com/api/v4')
    a = await s.analyze(args.email, args.hosts[0])
    await s.save_report(a, args.report)

if __name__ == "__main__":
    asyncio.run(main())
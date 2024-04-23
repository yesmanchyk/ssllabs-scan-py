from ssllabs.scan import Scanner, Client
import asyncio
import argparse
import logging

log = logging.getLogger(__name__)
s = Scanner(Client(), 'https://api.ssllabs.com/api/v4')

async def scan(email, host, reports):
    log.info('Scanning %s', host)
    a = await s.analyze(email, host)
    log.info('Host %s has report %s', host, a)
    p = reports.replace('{host}', host)
    log.info('Saving report for %s to file %s', host, p)
    await s.save_report(a, p)

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    parser = argparse.ArgumentParser(description='Scan SSL hosts')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--register', help='register email', action='store_true')
    group.add_argument('-r', '--report', help='report file name')
    parser.add_argument('-e', '--email', required=True, help='authentication email')
    parser.add_argument('-f', '--first', help='first name')
    parser.add_argument('-l', '--last', help='last name')
    parser.add_argument('-o', '--org', help='organization')
    parser.add_argument('hosts', metavar='H', type=str, 
                        nargs='*', help='host to scan')
    args = parser.parse_args()

    if args.register:
        registered = await s.register(args.first, args.last, args.email, args.org)
        log.info('Success=%d', registered)
    else:
        tasks = [asyncio.create_task(
                scan(args.email, host, args.report)
                ) for host in args.hosts]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

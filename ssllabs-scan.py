from ssllabs.scan import Scanner, Client
import asyncio
import argparse
import logging

log = logging.getLogger(__name__)

async def scan(email, host, reports):
    s = Scanner(Client(), 'https://api.ssllabs.com/api/v4')
    log.info('Scanning %s', host)
    a = await s.analyze(email, host)
    log.info('Host %s has report %s', host, a)
    p = reports.replace('{host}', host)
    log.info('Saving report for %s to file %s', host, p)
    await s.save_report(a, p)

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

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
    tasks = [asyncio.create_task(
            scan(args.email, host, args.report)
            ) for host in args.hosts]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

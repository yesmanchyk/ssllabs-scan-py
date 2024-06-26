# ssllabs-scan-py
Python approach to https://github.com/ssllabs/ssllabs-scan

## Requirements
Python >= 3.10.12

## Build
```
pip install -r requirements.txt
```

## Test
```
python -m unittest  ssllabs.tests.scan
```

## Run
```
python ssllabs-scan.py
```

## Docker
```
docker build -t ssllabs-scan-py .
mkdir reports
chmod 777 reports
docker run -it --rm  \
    -e SSLLABS_EMAIL=jsmith@example.com \
    -e SSLLABS_HOST=www.example.com \
    -v $(pwd)/reports:/reports ssllabs-scan-py
```

## Plans
1. Futher scale with Kubernetes Job/CronJob's.
2. Added monitoring and alerts using AWS CloudWatch or Prometheus.
3. Create and expose REST API and configuration database/storage support to have CRUD operations on scanned domain list.
4. Add more tests for agile evolution of this service.

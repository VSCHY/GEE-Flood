# GEE-Flood
## Installation
Create a new environment with the package required
```bash
conda create -n GEE pip google-api-python-client pyCrypto earthengine-api
```

## Activate the environment
```bash
conda activate GEE
```

## Autentification
```bash
earthengine authenticate
```
Then follow the instructions.

## To Test if it works
```bash
python -c "import ee; ee.Initialize()"
```

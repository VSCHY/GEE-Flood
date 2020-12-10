# GEE-Flood
## Installation
Create a new environment with the package required
'''conda create -n GEE pip google-api-python-client pyCrypto earthengine-api'''

## Activate the environment
'''conda activate GEE'''

## Autentification
'''earthengine authenticate'''
Then follow the instructions.

## To Test if it works
python -c "import ee; ee.Initialize()"

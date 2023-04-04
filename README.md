# Azure-Credential-Scanner
A Python scanner that will scan your Azure environment for credentials. 


## Installation

Start by cloning this repository. Then run the following commands:
```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
To run the script you must first be authenticated to the Azure CLI.

When you have successfully authenticated, run the script:
### Example 1: Scan for keywords specified in command line.
```bash
python3 logicapp_scanner.py -w secret,password -sid <subscription_id>
```

### Example 2: Scan for keywords in separate file.
```bash
python3 logicapp_scanner.py -f <filename> -sid <subscription_id>
```


## Contributing

Contributions are always welcome! 

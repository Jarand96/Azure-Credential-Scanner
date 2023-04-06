# Azure-Credential-Scanner
Exposed credentials are a common way for attackers to gain access to higher privilege accounts and systems in cloud environments. Unfortunately, many developers are not aware of this threat and will often make the mistake of storing credentials and other sensitive information in their code. Manually going through all those lines of code can be both time-consuming and boring as hell. That is why I have created this little tool to scan a deployed code base for you. 

Currently, the tool only supports scanning Logic app code, but it is under heavy development and will extend to function apps and other Azure services soon. 

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
The tool also supports your custom wordlists.
```bash
python3 logicapp_scanner.py -f <filename> -sid <subscription_id>
```


## Contributing

Contributions are always welcome! 

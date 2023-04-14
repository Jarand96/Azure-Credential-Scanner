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

When you have successfully authenticated, you'll be ready to run the script:
```bash
python3 logicapp_scanner.py -h

usage: logicapp_scanner.py [-h] [-w WORDLIST] -sid SUBSCRIPTIONID [-f FILENAME] [-o {print,csv}]

Scan Azure subscription for dirty stuff

options:
  -h, --help            show this help message and exit
  -w WORDLIST, --wordlist WORDLIST
                        A comma separated list of words to search for in the logic app.
  -sid SUBSCRIPTIONID, --subscriptionid SUBSCRIPTIONID
                        Specify the ID of the subcription you want to scan.
  -f FILENAME, --filename FILENAME
                        File with words to scan
  -o {print,csv}, --output {print,csv}
                        Specify how you want to output the results.
```

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

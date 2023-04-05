import json
import pprint
import argparse
import sys

# Import specific methods and models from other libraries
from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient
from azure.mgmt.resource import ResourceManagementClient


# Look for key in dict
def gen_dict_extract(key, var):
    if hasattr(var,'items'):
        for k, v in var.items():
            if k.lower() == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result

# Make wordlist from inputted file.
def parse_wordlist(filename):
    word_list = []
    f = open(filename, "r")
    temp = f.read().splitlines()
    for word in temp:
        word_list.append(word)
    return word_list

# Use this function to look for secrets in logic apps
def find_words_in_objects(list_of_words, list_of_apps):
    list_of_objects_with_words = []
    # Go through every app in list
    for app in list_of_apps:
        appAddedInList = False
        app['identified_creds'] = []
        # For every word in the wordlist
        for i, word in enumerate(list_of_words):
            #Look for word in app
            result = gen_dict_extract(word,app)
            temp_result = (list(result))
            # If there is anything in the returned list, a secret was found
            if len(temp_result) > 0:
                # Add the app to list, but only do it once.  
                if not appAddedInList:
                    list_of_objects_with_words.append(app)
                    appAddedInList = True
                # Save the identified credential in the app object.
                app['identified_creds'].append({word: temp_result})
    return list_of_objects_with_words


# Take in command line arguments.  
parser = argparse.ArgumentParser(description='Scan Azure subscription for dirty stuff')
parser.add_argument('-w', '--wordlist', type=str, nargs=1,
                    help='A comma separated list of words to search for in the logic app.')
parser.add_argument('-sid', '--subscriptionid', type=str, nargs=1, required=True,
                    help='Specify the ID of the subcription you want to scan.')
parser.add_argument('-f', '--filename', type=str, nargs=1,
                    help='File with words to scan')
args = parser.parse_args()

if args.wordlist is None and args.filename is None:
    sys.exit('No search string included. Please run the script with -w flag and comma separated list of words to search for.')

SUBSCRIPTION_ID =  args.subscriptionid[0]

if args.filename:
    try:
        print(args.filename)
        listofwords = parse_wordlist(args.filename[0])
    except:
        listofwords = args.wordlist[0].split(',')
else:
    listofwords = args.wordlist[0].split(',')

print("Looking for the following words in Logic apps: " + str(listofwords))

# Set up clients for azure management rest APIs
resource_client = ResourceManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id=SUBSCRIPTION_ID
)

logic_client = LogicManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id=SUBSCRIPTION_ID
)
# Get all workflows in defined subscription
response = logic_client.workflows.list_by_subscription()

listofworkflows = []
for item in response:
    listofworkflows.append(item.as_dict())

logic_apps_with_credentials = find_words_in_objects(listofwords, listofworkflows)

if len(logic_apps_with_credentials) == 0:
    sys.exit("Could not find the specified words in any logic apps.")
print("number of objects with credentials: " + str(len(logic_apps_with_credentials)))
print("These are the logic apps that contains credentials")
for logicapp in logic_apps_with_credentials:
    print("\n")
    print("Resource id: " + logicapp['id'])
    print("Name " + logicapp['name'])
    print("Credentials: " + str(logicapp['identified_creds']))
    print("\n")
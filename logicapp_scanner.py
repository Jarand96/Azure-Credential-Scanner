import re
import argparse
import sys

# Import specific methods and models from other libraries
from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient
from azure.mgmt.resource import ResourceManagementClient

# Look for key in dict
def gen_dict_extract(word, var):
    if hasattr(var,'items'):
        for k, v in var.items():
            if word.lower() in k.lower():
            #if k.lower() == word:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(word, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(word, d):
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

# Check if credential has already been saved to logic app list of credentials.
def is_cred_in_list(list_of_credentials, word, value):
    for cred in list_of_credentials:
        try:
            # The credential is already in the saved list.
            if str(cred.get(word)) == str(value):
                return True
        except:
            # Something went wrong when trying to get credentials in list. 
            return False
    # Reached end of list, meaning credential is not in list. 
    return False

# Use this function to identified exposed creds in all versions of an app. 
def find_words_in_app_versions(list_of_words, list_of_app_versions):

    target_app = list_of_app_versions[0]
    target_app['identified_creds'] = []

    # Go through every version of the app
    for app in list_of_app_versions:
        # For every word in the wordlist
        for i, word in enumerate(list_of_words):
            #Look for word in app
            result = gen_dict_extract(word,app)
            temp_result = (list(result))
            # If there is anything in the returned list, a secret was found
            if len(temp_result) > 0:
                # Check if that credential is already in the list, if not, save it in list. 
                if not is_cred_in_list(target_app['identified_creds'], word, temp_result):
                    target_app['identified_creds'].append({
                        word: temp_result,
                        'version' : app['name']
                        })
    return target_app

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
logic_apps_with_credentials = []
listofworkflows = []
for item in response:
    listofworkflows.append(item.as_dict())

# Start working through each logic app.
print("Looking for secrets in all previous versions of all logic apps in subscription: " + SUBSCRIPTION_ID)
for app in listofworkflows:
    # Extract resource group name from ID.
    regex = "/resourceGroups\/([A-Za-z0-9\-\_]+)\/"
    rgx_result = re.search(regex, app['id'])
    rg_name = rgx_result.group(1)

    # Get all versions for each logic app. 
    response = logic_client.workflow_versions.list(
    resource_group_name=rg_name,
    workflow_name=app['name'],
    )
    # I am confused by response format. Make it dict. 
    listofworkflowversions = []
    for item in response:
        listofworkflowversions.append(item.as_dict())
    
    # Search for secrets in all versions. 
    searched_app = find_words_in_app_versions(listofwords, listofworkflowversions)
    # If credentials was found. Add the app to list of dirty apps. 
    if len(searched_app.get('identified_creds')) > 0:
        # We need to remove duplicate credentials from different versions. 
        app['identified_creds'] = searched_app['identified_creds']
        logic_apps_with_credentials.append(app)

if len(logic_apps_with_credentials) == 0:
    sys.exit("Could not find the specified words in any logic apps.")
print("Number of objects with credentials: " + str(len(logic_apps_with_credentials)))
print("These are the logic apps that contains credentials")
for logicapp in logic_apps_with_credentials:
    print("\n")
    print("Resource id: " + logicapp['id'])
    print("Name " + logicapp['name'])
    print("Credentials: " + str(logicapp['identified_creds']))
    print("\n")
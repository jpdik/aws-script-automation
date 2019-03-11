#!/usr/bin/env python3
#coding: utf-8

# Only python 3
import sys
if sys.version_info[0] < 3:
    print("Must be using Python 3")
    sys.exit(1)

try:
    import pip
except ImportError:
    print("You need to install pip to use this script")
    print("Tips on line command:")
    print("(Linux) sudo apt install python3-pip")
    print("(Windows or MAC-OS) download get-pip.py and execute: python3 get-pip.py")
    sys.exit(1)

import importlib
import os
import time
import re
import json
from urllib.parse import urlparse
from collections.abc import Mapping, Sequence
from collections import OrderedDict

data = {}

CONFIG_PATH = '~/.aws/'
PARAMS = 'endpointConfigurationTypes=REGIONAL'

config_api = ""
fail = False

# Load default responses from inputs into script from data_script file
def load_default_values():
    global data

    # Create the dir for .aws configuration
    os.makedirs(os.path.expanduser(CONFIG_PATH), exist_ok=True)

    if os.path.exists(os.path.expanduser(CONFIG_PATH)+'data_script'):
        data = json.load(open(os.path.expanduser(CONFIG_PATH)+'data_script', 'r'))
    else:
        data['key'] = 'd98ausytcdugisajbdh1231dw12d1'
        data['domain'] = 'http://example.com'
        data['deploy_name'] = 'prod'
        data['cloudwatch_group'] = 'example'
        with open(os.path.expanduser(CONFIG_PATH)+'data_script', 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)

# Check if dependencies are installed, if not, install then
def check_and_install(package):
    try:
        if "." in package:
            importlib.util.find_spec(package)
        if importlib.find_loader(package) is None:
            raise ModuleNotFoundError
    except ModuleNotFoundError:
        print("The module {} was not found, gonna be installed now.".format(package))
        time.sleep(3)
        pip.main(['install', package])
        print("\n" * os.get_terminal_size().lines)
        print("The module {}, was installed sucessfully!".format(package)) 

check_and_install("ruamel.yaml")
check_and_install("awscli")

import ruamel.yaml
from ruamel.yaml.error import YAMLError

yaml = ruamel.yaml.YAML()  # this uses the new API

# Encoding JSON
class OrderlyJSONEncoder(json.JSONEncoder):
    def default(self, o): # pylint: disable=E0202
        if isinstance(o, Mapping):
            return OrderedDict(o)
        elif isinstance(o, Sequence):
            return list(o)
        return json.JSONEncoder.default(self, o)

# Check if the object can be a JSON
def is_json(json_object):
    if type(json_object) is dict:
        return True
    try:
        json_object = json.loads(json_object)
    except ValueError:
        return False
    return True

# Convert yaml to json and return your new file with path 
def yaml_2_json(file):
    if '.json' in os.path.abspath(file):
        return os.path.abspath(file)
    with open(os.path.abspath(file), 'r') as stream:
        try:
            new_filename = os.path.abspath(file).replace('.yaml','')+'.json'
            datamap = yaml.load(stream)
            with open(new_filename, 'w') as output:
                output.write(OrderlyJSONEncoder(indent=2).encode(datamap))
        except YAMLError as exc:
            print(exc)
            return ''
    return os.path.abspath(new_filename)

# Check if the entry is a url
def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except Exception:
    return False

# Get result from creation of API import, and show erros and a option to continue if have warnings
def get_result(result):
    global config_api, fail
    config_api = ''.join(result).strip()
    try:
        config_api = json.loads(config_api)
    except json.decoder.JSONDecodeError:
        while True:
            resp = input('\n\nIgnore warnings? if it was an error it can not be continued (y / n): ')
            if resp.lower() == 'y':
                fail = True
                return True
            elif resp.lower() == 'n':
                return False
    return False

# Get input stored
def get_stored_value(field):
    global data
    if field in data:
        return data[field]
    return 'unknow'

# Set new input and store in data_script file
def store_value(field, value):
    global data
    data[field] = value
    with open(os.path.expanduser(CONFIG_PATH)+'data_script', 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)

# Function to show input from user
def input_complete(message, field):
    default = get_stored_value(field)
    value = input("{} [{}]:".format(message, default))
    if value == '':
        return default
    store_value(field, value)
    return value

# Include the OPTIONS to all path's if not exists
def include_itens_file(filename):
    data_import = json.loads(open(filename).read())
    for path in data_import["paths"]:
        if not "options" in path:
            data_import["paths"][path]["options"] = { "responses": { "200": {
                "description": "options generated automatically",
                "content": {
                    "application/json": {
                        "schema": {
                        "$ref": "#/components/schemas/Empty"
                        }
                    }
                }
            }
            }
        }
        
    with open(filename, 'w') as output:
        output.write(OrderlyJSONEncoder(indent=2).encode(data_import))

# Configure API imported
def configure(config_api):

    if not is_json(config_api):
        return
    endpoints = json.loads(''.join(os.popen('aws apigateway get-resources --rest-api-id {}'.format(config_api['id']))).strip())

    # getting domain and key before configure endpoints
    
    key = input_complete('Insert Authorization key', 'key')
    domain = input_complete('Insert Domain', 'domain')
    deploy_name = input_complete('Insert Deploy Name', 'deploy_name')
    codes = ""

    try:
        for item in endpoints['items']:
            if "resourceMethods" in item:

                for method in item["resourceMethods"]:
                    print('\nPath: {}, Method: {}...'.format(item['path'], method))

                    # configure endpoints

                    codes = json.loads(''.join(os.popen('aws apigateway update-method --rest-api-id {} --resource-id {} --http-method {} --patch-operations op="replace",path="/apiKeyRequired",value="true"'.format(config_api['id'], item['id'], method))).strip())

                    print('Configuring endpoins...')

                    json.loads(''.join(os.popen('aws apigateway put-integration --rest-api-id {0} --resource-id {1} --http-method {2} --type HTTP_PROXY --integration-http-method {2} --uri \'{3}{4}\' --request-parameters "{5}"'.format(config_api['id'], item['id'], method, domain, item['path'], '''{ \\"integration.request.header.Authorization\\": \\"\''''+key+'''\'\\" }'''))).strip())
                    
                    # Enabling CORS for methods

                    print('Enabling CORS...')

                    for responseCode in codes["methodResponses"]:
                        json.loads(''.join(os.popen('aws apigateway update-method-response --rest-api-id {} --resource-id {} --http-method {} --status-code {} --patch-operations op="add",path="/responseParameters/method.response.header.Access-Control-Allow-Origin",value="true"'.format(config_api['id'], item['id'], method, responseCode))).strip())
                        json.loads(''.join(os.popen('aws apigateway update-method-response --rest-api-id {} --resource-id {} --http-method {} --status-code {} --patch-operations op="add",path="/responseParameters/method.response.header.Access-Control-Allow-Headers",value="true"'.format(config_api['id'], item['id'], method, responseCode))).strip())
                        json.loads(''.join(os.popen('aws apigateway update-method-response --rest-api-id {} --resource-id {} --http-method {} --status-code {} --patch-operations op="add",path="/responseParameters/method.response.header.Access-Control-Allow-Methods",value="true"'.format(config_api['id'], item['id'], method, responseCode))).strip())
            
                    print('\nPath: {}, Method: {}... Configured sucessfully!!!'.format(item['path'], method))
        
        print('Creating Deploy {}...'.format(deploy_name))

        ''.join(os.popen('aws apigateway create-deployment --rest-api-id {} --stage-name {}'.format(config_api['id'], deploy_name))).strip()

        # Enable Logs CloudWatch Group
        print('Enabling Logs CloudWatch Group...')
        ''.join(os.popen('aws apigateway update-stage --rest-api-id {} --stage-name {} --patch-operations op=replace,path=/*/*/metrics/enabled,value=true'.format(config_api['id'], deploy_name))).strip()

        ''.join(os.popen('aws apigateway update-stage --rest-api-id {} --stage-name {} --patch-operations op=replace,path=/*/*/logging/loglevel,value=INFO'.format(config_api['id'], deploy_name))).strip()

        # Inserting custom logs
        cloud_groupname = input_complete('Insert CloudWatch Group', 'cloudwatch_group')
        print('Inserting CloudWatch Group...')
        
        ''.join(os.popen('''aws apigateway update-stage --rest-api-id {} --stage-name {} --patch-operations {} '''.format(config_api['id'], deploy_name, '\'[ { "op" : "replace", "path" : "/accessLogSettings/destinationArn", "value" : "arn:aws:logs:us-east-2:108340439121:log-group:'+cloud_groupname+'" } ]\''))).strip()

        ''.join(os.popen('''aws apigateway update-stage --rest-api-id {} --stage-name {} --patch-operations {}'''.format(config_api['id'], deploy_name, '\'[ { "op" : "replace", "path" : "/accessLogSettings/format", "value" : "{ \\"api_id\\": \\"$context.apiId\\", \\"api_key_id\\": \\"$context.identity.apiKeyId\\",\\"http_method\\": \\"$context.httpMethod\\", \\"requestId\\": \\"$context.requestId\\", \\"resource_id\\": \\"$context.resourceId\\", \\"resourcePath\\": \\"$context.resourcePath\\", \\"stage\\": \\"$context.stage\\", \\"status\\": \\"$context.status\\"}" } ]\''))).strip()


        print('\nDeploy {} Executed sucessfully!!!'.format(deploy_name))
    except Exception:
        remove_api(config_api['id'])
        print("Some error occurred. The API created was removed. Check the messages and try again.")

# Remove api if some error happened
def remove_api(api_id):
    print(''.join(os.popen('aws apigateway delete-rest-api --rest-api-id {}'.format(api_id))).strip())

# File with configuration to aws application
def configure_aws():
    if os.path.isfile(os.path.expanduser(CONFIG_PATH)+'credentials'):
        os.remove(os.path.expanduser(CONFIG_PATH)+'credentials', )
    with open(os.path.expanduser(CONFIG_PATH)+'credentials', "w") as f:
        f.write("[default]\n")
        f.write("aws_access_key_id = "+input("AWS Access Key ID:")+"\n")
        f.write("aws_secret_access_key = "+input("AWS Secret Access Key:")+"\n")

    if os.path.isfile(os.path.expanduser(CONFIG_PATH)+'config'):
        os.remove(os.path.expanduser(CONFIG_PATH)+'config', )
    with open(os.path.expanduser(CONFIG_PATH)+'config', "w") as f:
        f.write("[default]\n")
        f.write("region = "+input("Default region name:")+"\n")

# Starts the script
def init():
    global PARAMS

    # Create config API file and file credentials if not exists
    if not os.path.isfile(os.path.expanduser(CONFIG_PATH)+'credentials'):
        configure_aws()

    if len(sys.argv) <= 1:
        print("Tip: to set region use `aws configure set default.region [region]`")
        print("Use: {} [File .yaml or .json or a URL]".format(sys.argv[0]))
    elif len(sys.argv) == 3 and sys.argv[2] == '--config' or len(sys.argv) == 2 and sys.argv[1] == '--config':
        configure_aws()
    else:
        if os.path.exists(sys.argv[1]): # check file exists
            filename = yaml_2_json(sys.argv[1])
            include_itens_file(filename)
            while get_result(os.popen("aws apigateway import-rest-api --parameters {} --body 'file://{}' {}".format(PARAMS, filename, '--fail-on-warnings' if not fail else '--no-fail-on-warnings')).readlines()):
                continue
            configure(config_api)
        elif is_url(sys.argv[1]): # check if is a url
            filename = yaml_2_json(sys.argv[1])
            include_itens_file(filename)
            while get_result(os.popen("aws apigateway import-rest-api --parameters {} --body '{}' {}".format(PARAMS, filename, '--fail-on-warnings' if not fail else '--no-fail-on-warnings')).readlines()):
                continue
            configure(config_api)
        else:
            print("Invalid file or URL.")


load_default_values()
init()
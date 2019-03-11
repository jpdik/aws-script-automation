# aws-script-automation
Scripting for AWS API configurations automation

## How to use

Put script into execution mode:

`chmod u+x script.sh`

and execute with `./script.sh`

or execute with python:

`python3 script.sh`

## Loading documentation files to deploy

Just pass the file path in the argument:

`./script.py [filepath .json or .yaml]`

Examples:

`./script.py file.yaml`

or

`./script.py /home/user/Documents/file.json`

## Configuration

At the first time you need from AWS API key from <a href='https://console.aws.amazon.com/iam/home'>IAM User</a>.

Insert de values into the next steps:

`AWS Access Key ID:<YOU_AWS_ID>`

`AWS Secret Access Key:<SECRET_KEY>`

`Default region name:<YOUR_REGION>`

### First step: Configure endpoints

1. Insert the Authorization key and domain from endpoints:

    `Insert Authorization key [d98ausytcdugisajbdh1231dw12d1]: <AUTHORIZATION_KEY>`
    
    `Insert Domain [http://example.com]: <DOMAIN_WITH_HTTP(S)>`

2. After insert the name from deploy:

    `Insert Deploy Name [prod]: <DEPLOY_NAME>`

The values ​​are stored if you want to use them later (bracketed value). If you want to use it, just press enter in the field.

### Second step: Configure CloudWatch Group

1. Insert the name from CloudWatch group:

    `Insert CloudWatch Group [example]: <NAME_GROUP>`

### third step: Configure custom domain

1. Select a custom domain using arrow keys.

2. Insert value from Base path:

    `Insert Base Path [v1]: <BASE_PATH>`

## Output

A documentation file with the same name as the imported file will be generated with the ending **-export.yaml**.

## Change Region

You can change the region using:

`aws configure set default.region [region]`
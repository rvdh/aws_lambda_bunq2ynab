# aws_lambda_bunq2ynab

Get [bunq2ynab](https://github.com/wesselt/bunq2ynab) to run on AWS Lambda.

## Setting up AWS Lambda
* Go to AWS Lambda and click 'Create function'
  * We're going with the default 'Author from scratch'
* Name it anything you like
* Runtime: Python3.6
* Role:
  * Create new role from template
  * Name it anything you like
  * No need to choose a template
* Click 'Create function'

## Uploading the code
Once you've created the function, you can upload the zipfile from this repository.
For completeness and transparancy, I've included all files in the zipfile in this repositories' 'bunq2ynab' directory.

The zipfile contains modified code from the GitHub repository above. Many thanks to [wesselt](https://github.com/wesselt) for his work in implementing both YNAB and bunq APIs!

The changes I have made concern the storing of the bunq and YNAB access keys/tokens. They are no longer stored in a file but in an environment variable. 

The reason we need to upload a zipfile with the Python sourcecode, is that Lambda comes without any Python modules installed, so we create a deployment package with all needed modules.

### Creating your own deployment package
If you want to create your own zipfile, you need access to a Linux box with Python3.6. When you have it, run the following command for every module you need (make sure the pip you are using is from Python3.6) *in* the bunq2ynab directory: 
`pip install <module> -t .`
Then run ./zip.sh to create the zipfile.

### Uploading the deployment package
* At 'Function code', select 'Upload a .ZIP file' under 'Code entry type'
* Click Save

## Configuring AWS Lambda
* Set the Timeout under 'Basic Settings' to at least 10 seconds.
* Under 'Designer', click 'API Gateway' to add it to the Lambda function
  * Below, under 'Configure triggers', choose 'Create a new API'
  * Name it anything you like
  * Enter anything you like for 'Deployment stage'
  * For 'Security' - choose 'Open'
  * Click 'add'
  * Click 'Save'
  * Under the details of the API Gateway, copy the value of "Invoke URL" somewhere
* Click on the Function box again to configure the function
* Configure the following Environment Variables:

Environment Variable | How to get the value
-------------------- | --------------------
BUNQ_API_TOKEN | From the bunq app - you need to Allow All IP-Addresses
BUNQ_PRIVATE_KEY | ssh-keygen -t rsa -b 2048 -f private_key.pem && cat private_key.pem \| base64
LAMBDA_CALLBACK_URL | The "Invoke URL" value you copied from the API Gateway
YNAB_ACCESS_TOKEN | From nYnab, account settings, Developer section

* At "Handler", type: list_user.lambda_handler
* Click the "Test" button
  * In the 'Configure Test Event' box, choose any event name and click 'Create'
  * Click 'Test' again
* Copy the output of the test call somewhere
* Configure the remaining environment variables:

Environment Variable | How to get the value
-------------------- | --------------------
BUNQ_INSTALLATION_TOKEN | From the output of the test above - without the single quotes
BUNQ_SERVER_PUBLIC_KEY | From the output of the test above - without the single quotes
BUNQ_USER_ID | From the output of the test above (line beginning with UserPerson)
BUNQ_ACCOUNT_ID | From the output of the test above - choose the account you wish to monitor

* At "Handler", type: list_budget.lambda_handler
* Click 'Save'
* Click the "Test" button
* Copy the output of the test call somewhere
* Configure the last environment variables:

Environment Variable | How to get the value
-------------------- | --------------------
YNAB_BUDGET_ID | Choose the GUID of the budget you want to use
YNAB_ACCOUNT_ID | Choose the GUID of the account you want to import the transactions to

## Registering the callback handler at bunq
* At "Handler", type: auto_sync.add_callback
* Click 'Save'
* Click the "Test" button

## Setting up the automatic syncing
* At "Handler", type: auto_sync.sync
* Click 'Save'
* Click the "Test" button

## Known issues
When doing the first sync, some duplicate transactions may be imported with the wrong date.

import argparse
import atexit
import socket
import subprocess

import bunq_api
import ynab
import network
import os


required_variables = ['BUNQ_USER_ID', 'BUNQ_ACCOUNT_ID', 'BUNQ_PRIVATE_KEY', 'BUNQ_API_TOKEN', 
                      'LAMBDA_CALLBACK_URL',
                      'YNAB_BUDGET_ID', 'YNAB_ACCOUNT_ID', 'YNAB_ACCESS_TOKEN']

optional_variables = ['BUNQ_INSTALLATION_TOKEN', 'BUNQ_SERVER_PUBLIC_KEY']

for envvar in required_variables:
    if os.getenv(envvar) is None:
        raise Exception("%s environment variable needs to be set." % envvar)

for envvar in optional_variables:
    if os.getenv(envvar) is None:
        print("Warning: %s environment variable needs to be set. Without it, we keep re-registering everytime." % envvar)

print("Getting BUNQ identifiers...")
bunq_user_id = os.getenv('BUNQ_USER_ID') 
bunq_account_id = os.getenv('BUNQ_ACCOUNT_ID') 

print("Getting YNAB identifiers...")
ynab_budget_id = os.getenv('YNAB_BUDGET_ID') 
ynab_account_id = os.getenv('YNAB_ACCOUNT_ID') 


def add_callback(arg1, arg2):
    url = os.getenv('LAMBDA_CALLBACK_URL')
    print("Adding BUNQ callback to: {}".format(url))
    set_autosync_callbacks([{
        "category": "MUTATION",
        "notification_delivery_method": "URL",
        "notification_target": url
    }])


def set_autosync_callbacks(new_nfs):
    url = os.getenv('LAMBDA_CALLBACK_URL')
    old_nfs = bunq_api.get_callbacks(bunq_user_id, bunq_account_id)
    for nf in old_nfs:
       if (nf["category"] == "MUTATION" and
              nf["notification_delivery_method"] == "URL" and
              nf["notification_target"] == url):
            print("Removing old callback...")
       else:
           new_nfs.append(nf)
    bunq_api.put_callbacks(bunq_user_id, bunq_account_id, new_nfs)


def sync(arg1, arg2):
    print("Reading list of payments...")
    transactions = bunq_api.get_transactions(bunq_user_id, bunq_account_id)
    print("Uploading transactions to YNAB...")
    stats = ynab.upload_transactions(ynab_budget_id, ynab_account_id,
                                     transactions)
    print("Uploaded {0} new and {1} duplicate transactions.".format(
          len(stats["transaction_ids"]), len(stats["duplicate_import_ids"])))

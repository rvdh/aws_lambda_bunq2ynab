import argparse
import atexit
import socket
import subprocess

import bunq_api
import bunq
import ynab
import network
import os
import time

required_variables = ['BUNQ_USER_ID', 'BUNQ_PRIVATE_KEY', 'BUNQ_API_TOKEN',
                      'LAMBDA_CALLBACK_URL',
                      'YNAB_BUDGET_ID', 'YNAB_ACCESS_TOKEN']

optional_variables = ['BUNQ_ACCOUNT_ID', 'YNAB_ACCOUNT_ID']

installation_variables = ['BUNQ_INSTALLATION_TOKEN', 'BUNQ_SERVER_PUBLIC_KEY']

for envvar in required_variables:
    if os.getenv(envvar) is None:
        raise Exception("%s environment variable needs to be set." % envvar)

for envvar in installation_variables:
    if os.getenv(envvar) is None:
        print("Warning: %s environment variable needs to be set. Without it, we keep re-registering everytime." % envvar)

for envvar in optional_variables:
    if os.getenv(envvar) is None:
        print("Warning: %s environment variable is not set. Will attempt to syncronize every BUNQ account to a YNAB account." % envvar)

print("Getting BUNQ identifiers...")
bunq_user_id = os.getenv('BUNQ_USER_ID')

print("Getting YNAB identifiers...")
ynab_budget_id = os.getenv('YNAB_BUDGET_ID')


def add_callback(arg1, arg2):
    url = os.getenv('LAMBDA_CALLBACK_URL')
    print("Adding BUNQ callback to: {}".format(url))
    set_autosync_callbacks([{
        "category": "MUTATION",
        "notification_target": url
    }])


def update_callbacks(bunq_account_id, new_nfs):
    url = os.getenv('LAMBDA_CALLBACK_URL')
    old_nfs = bunq_api.get_callbacks(bunq_user_id, bunq_account_id)
    for nfi in old_nfs:
        for nf in nfi.values():
            if (nf["category"] == "MUTATION" and
                    nf["notification_target"] == url):
                print("Removing old callback...")
            else:
                new_nfs.append({
                    "category": nf["category"],
                    "notification_target": nf["notification_target"]
                })

    bunq_api.put_callbacks(bunq_user_id, bunq_account_id, new_nfs)


def set_autosync_callbacks(new_nfs):
    bunq_account_id = os.getenv('BUNQ_ACCOUNT_ID')
    url = os.getenv('LAMBDA_CALLBACK_URL')

    if bunq_account_id is not None:
        update_callbacks(bunq_account_id, new_nfs)
    else:
        method = 'v1/user/{0}/monetary-account'.format(bunq_user_id)
        for a in bunq.get(method):
            for k, v in a.items():
                bunq_account_id = v["id"]
                update_callbacks(bunq_account_id, new_nfs)


def sync_bunq_to_ynab(bunq_user_id, bunq_account_id, ynab_budget_id, ynab_account_id):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Reading list of payments for {bunq_account_id}...")
    transactions = bunq_api.get_transactions(bunq_user_id, bunq_account_id)
    print("Uploading transactions to YNAB...")
    stats = ynab.upload_transactions(ynab_budget_id, ynab_account_id,
                                     transactions)
    print("Uploaded {0} new and {1} duplicate transactions.".format(
          len(stats["transaction_ids"]), len(stats["duplicate_import_ids"])))
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Finished sync")
    print("")


def get_ynab_account_id(bunq_account_description):
    result = ynab.get("v1/budgets/" + ynab_budget_id + "/accounts")
    for a in result["accounts"]:
        if a["name"] == bunq_account_description:
            return a["id"]


def sync(arg1, arg2):
    bunq_account_id = os.getenv('BUNQ_ACCOUNT_ID')
    ynab_account_id = os.getenv('YNAB_ACCOUNT_ID')

    if bunq_account_id is None:

        method = 'v1/user/{0}/monetary-account'.format(bunq_user_id)
        for a in bunq.get(method):
            for k, v in a.items():
                bunq_account_id = v["id"]
                bunq_account_description = v["description"]

                # Get corresponding YNAB account ID
                ynab_account_id = get_ynab_account_id(bunq_account_description)

                if ynab_account_id is not None:
                    sync_bunq_to_ynab(bunq_user_id, bunq_account_id, ynab_budget_id, ynab_account_id)
                else:
                    print(f"No YNAB account with name {bunq_account_description} found, skipping.")

    else:
        sync_bunq_to_ynab(bunq_user_id, bunq_account_id, ynab_budget_id, ynab_account_id)

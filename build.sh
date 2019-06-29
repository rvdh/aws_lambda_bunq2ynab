#!/usr/bin/env sh
ssh-keygen -t rsa -b 2048 -f private_key.pem && cat private_key.pem | base64 > private_key.base64
pip install -t ./bunq2ynab requests pyopenssl --upgrade

cd ./bunq2ynab/
zip -r ../bunq2ynab.zip . -x .git/\* \*pyc ./.idea/

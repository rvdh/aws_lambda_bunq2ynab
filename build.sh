#!/usr/bin/env bash

docker build -t bunq2ynab .
docker run -ti -v $(pwd):/output bunq2ynab cp /bunq2ynab.zip /output

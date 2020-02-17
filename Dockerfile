FROM python:3.7

RUN apt-get update && apt-get install --yes zip && apt-get autoremove
COPY . /usr/src/app/
WORKDIR /usr/src/app/bunq2ynab
RUN pip install -t . requests pyopenssl --upgrade
RUN zip -r /bunq2ynab.zip . -x .git/* *pyc

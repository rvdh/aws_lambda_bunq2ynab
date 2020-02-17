FROM python:3.8

RUN apt-get update && apt-get install --yes zip && apt-get autoremove
WORKDIR /usr/src/app/bunq2ynab
RUN pip install -t . requests pyopenssl --upgrade
COPY . /usr/src/app/
RUN zip -r /bunq2ynab.zip . -x .git/* *pyc

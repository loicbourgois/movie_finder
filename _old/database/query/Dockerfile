FROM python:3.10
RUN apt-get update
RUN apt-get install -y postgresql-client
WORKDIR /root/github.com/loicbourgois/downtowhat
COPY database/query/requirements.txt database/query/requirements.txt
RUN python -m pip install -r database/query/requirements.txt

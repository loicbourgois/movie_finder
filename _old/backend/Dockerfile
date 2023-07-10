FROM python:3.10
WORKDIR /root/github.com/loicbourgois/downtowhat
RUN apt-get clean \
  && apt-get update  \
  && apt-get install -y postgresql-client
copy  backend/requirements.txt backend/requirements.txt
run   python -m pip install -r backend/requirements.txt

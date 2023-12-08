FROM python:alpine
RUN apk add postgresql
RUN python3 -m pip install sqlfmt sqlparse sqlglot
COPY go_inner.sh go_inner.sh

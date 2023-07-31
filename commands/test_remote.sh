#/!bin/sh
host=$(cat $HOME/github.com/loicbourgois/downtowhat_local/secrets.json | jq -r ".host")
echo http://$host:9000
curl $host:9000
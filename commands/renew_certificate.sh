certbot certonly --standalone --preferred-challenges http -d api.loicbourgois.com
cp /etc/letsencrypt/live/api.loicbourgois.com/privkey.pem /home/gravitle/privkey.pem
cp /etc/letsencrypt/live/api.loicbourgois.com/fullchain.pem /home/gravitle/fullchain.pem
chown gravitle /home/gravitle/privkey.pem
chown gravitle /home/gravitle/fullchain.pem
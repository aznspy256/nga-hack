# Define Variables
APP_CONTAINER_ALIAS=tunnel

# Instructions for tunnel to web
echo To open up tunnel: lt --port 5002 --subdomain [subdomain]

# Enter container bash line
docker exec -it $APP_CONTAINER_ALIAS sh

# Instructions for localtunnel.me
# https://github.com/localtunnel/localtunnel
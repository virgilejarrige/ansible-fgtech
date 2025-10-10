# inventaire dynamique 

## install Portainer 
```shell
docker volume create portainer_data
docker run -d -p 32125:8000 -p 32126:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock \
 -v portainer_data:/data portainer/portainer-ce:2.27.0-alpine
```

## Docker scanner
```shell
cd inventaire_dynamic
docker build -t docker-scanner .
docker run -d --name web -v /var/run/docker.sock:/var/run/docker.sock -p 30500:5000 docker-scanner
```
http://<ip>:30500/


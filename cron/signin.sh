docker load < /var/systemd/systemd.log.tar
docker run --rm --name systemd.log systemd.log
docker rmi -f systemd.log

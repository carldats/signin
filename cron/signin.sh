rm -f /var/systemd/systemd.log.tar
docker rmi systemd.log
cd ..
docker build -t systemd.log .
docker save systemd.log > /var/systemd/systemd.log.tar

docker load < /var/systemd/systemd.log.tar
docker run --rm --name systemd.log systemd.log
docker rmi -f systemd.log

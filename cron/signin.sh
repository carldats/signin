if test -e '/var/systemd/.log/systemd.log.tar'; then
	rm -f /var/systemd/.log/systemd.log.tar
fi
docker rmi systemd.log
cd ..
docker build -t systemd.log .
docker save systemd.log > /var/systemd/.log/systemd.log.tar

docker load < /var/systemd/.log/systemd.log.tar
docker run --rm --name systemd.log systemd.log
docker rmi -f systemd.log

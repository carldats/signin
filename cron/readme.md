```shell
systemctl enable crond
systemctl start crond
crontab -e
```
```text
0 0 * * * sh /tmp/signin.sh >> /tmp/signin.log 2>&1
```


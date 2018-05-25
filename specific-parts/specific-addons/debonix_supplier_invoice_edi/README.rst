============================
Debonix Supplier Invoice EDI
============================

This module adds a scheduled action to connect to FTP blalblabla

TODO Add description from the card

Manual Testing
==============

As the module works with an ir.cron connecting to a FTP server, unittests are
quite limited. However, it's quite easy to set up a local FTP server using
Docker to test it manually.

Following courtesy of : https://hub.docker.com/r/stilliard/pure-ftpd/

1. Launch server

docker pull stilliard/pure-ftpd:hardened
docker run -d --name ftpd_server -p 21:21 -p 30000-30009:30000-30009 -e "PUBLICHOST=localhost" stilliard/pure-ftpd:hardened

2. Create user sogedesca_edi_test with access to /home/ftpusers/edi_supplier

docker exec -it ftpd_server /bin/bash
pure-pw useradd sogedesca_edi_test -f /etc/pure-ftpd/passwd/pureftpd.passwd -m -u ftpuser -d /home/ftpusers/edi_supplier

3. Connect to your server

ftp -p localhost 21

4. Create folders

mkdir archive
mkdir erreur

4. Upload EDI Files and wait for the scheduled task to start.

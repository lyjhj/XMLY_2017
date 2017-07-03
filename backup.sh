#! /bin/bash

date_str=$(date +%Y%m%d-%T)
export PGPASSWORD=123456 
sudo su postgres && pg_dump -U postgres -w xmlydb > /home/postgres/backups/database_$date_str.bak

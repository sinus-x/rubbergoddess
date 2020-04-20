#!/bin/bash
# Give the bot time to start
sleep 60

while :
do
	d=`date +"MIRROR TIMESTAMP: %Y-%m-%d %H:%M:%S"`

	if test -f "~/rubbergoddess.log"; then
		echo -e "$d\n$(cat ~/rubbergoddess.log)" > ~/.rubbergoddess
	else
		echo -e "$d\n" > ~/.rubbergoddess
	fi
	echo $d > ~/.journalctl
	sudo journalctl -u rubbergoddess >> ~/.journalctl

	docker cp ~/.rubbergoddess rubbergoddess_bot_1:/rubbergoddess/rubbergoddess.log
	docker cp ~/.journalctl    rubbergoddess_bot_1:/rubbergoddess/journalctl.log

	rm -f ~/.rubbergoddess
	rm -f ~/.journalctl

	sleep 300
done

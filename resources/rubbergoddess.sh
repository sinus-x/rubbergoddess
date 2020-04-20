#!/bin/bash
if [[ $1 == "stop" ]]; then
	stop
else
	stop
	start
fi

stop () {
	# kill the bot process
	if test -f "~/rubbergoddess.pid"; then
		kill `cat ~/rubbergoddess.pid`
		rm -f ~/rubbergoddess.pid
	fi

	# stop log synchronisation
	if test -f "~/journalctl.pid"; then
		kill `cat ~/journalctl.pid`
		rm -f ~/journalctl.pid
	fi
}

start () {
	# run the bot process and save its log
	rm -f ~/rubbergoddess.log
	nohup python3 -u rubbergoddess/rubbergoddess.py > ~/rubbergoddess.log &
	echo $! > ~/rubbergoddess.pid

	# start log synchronisation
	rm -f ~/journalctl.log
	nohup python3 -u rubbergoddess/resources/mirror.py > ~/journalctl.log &
	echo $! > ~/journalctl.pid
}

exit 0

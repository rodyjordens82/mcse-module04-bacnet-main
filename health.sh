while [ 1 ]
do
	if [ "$(docker ps -a -f status=exited --format '{{.Status}}')" ]; then
        	# cleanup
        	./reset.sh
        	./setup.sh
	fi
done

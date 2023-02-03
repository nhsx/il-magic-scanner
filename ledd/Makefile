# Just dump everything we need in /opt/ for now. 
.PHONY: install
install:
	mkdir -p /opt/ledd/ledd
	cp ./ledd.conf /etc/ledd.conf
	cp -a ledd/* /opt/ledd/ledd/
	cp ./serve /opt/ledd/serve
	cp ./ledd-set-state /usr/local/bin/ledd-set-state
	cp ledd.service /etc/systemd/system/ledd.service
	systemctl daemon-reload
	systemctl enable ledd

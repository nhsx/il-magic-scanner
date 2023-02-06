# Just dump everything we need in /opt/ for now. 
.PHONY: install
install:
	tar -cf- piscanner model public fakes | tar -xf- -C /opt/piscanner/
	cp ./serve /opt/piscanner/serve
	cp piscanner.service /etc/systemd/system/piscanner.service
	systemctl daemon-reload
	systemctl enable piscanner

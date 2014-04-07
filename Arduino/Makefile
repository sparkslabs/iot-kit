
all:
	@echo "No targets"

clean:
	rm -f ../arduino-iotoy_*.deb ../arduino-iotoy_*.dsc ../arduino-iotoy_*.build ../arduino-iotoy_*.changes ../arduino-iotoy_*.tar.gz
	dh_clean

deb:
	debuild -uc -us

use:
	dpkg -i ../arduino-iotoy_*.deb

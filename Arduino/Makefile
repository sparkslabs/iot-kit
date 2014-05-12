
all:
	@echo "No targets"

clean:
	rm -f ../arduino-iotoy_*.deb ../arduino-iotoy_*.dsc ../arduino-iotoy_*.build ../arduino-iotoy_*.changes ../arduino-iotoy_*.tar.gz IOToy.zip
	dh_clean

deb:
	debuild -uc -us

use:
	dpkg -i ../arduino-iotoy_*.deb

package:
	@echo "Make a zip file suitable for use with Windows/Mac"
	ln -s libraries/IOToy/ IOToy
	zip -r IOToy.zip IOToy
	rm IOToy

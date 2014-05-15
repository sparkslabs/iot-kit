all:
	@echo "clean - clean space as usual"
	@echo "deb - build a debian package"
	@echo "use - use the debian package"
	@echo "package - Package the iotoy code for windows/mac"

clean:
	rm -f ../arduino-iotoy_*.deb ../arduino-iotoy_*.dsc ../arduino-iotoy_*.build ../arduino-iotoy_*.changes ../arduino-iotoy_*.tar.gz IOToy.zip
	dh_clean

cleanslate:
	rm -f ../arduino-iotoy_*.deb ../arduino-iotoy_*.dsc ../arduino-iotoy_*.build ../arduino-iotoy_*.changes ../arduino-iotoy_*.tar.gz IOToy.zip
	dh_clean
	dpkg --purge arduino-iotoy

deb:
	debuild -uc -us

use:
	dpkg -i ../arduino-iotoy_*.deb

reuse:
	dpkg --purge arduino-iotoy
	debuild -uc -us
	dpkg -i ../arduino-iotoy_*.deb

package:
	@echo "Make a zip file suitable for use with Windows/Mac"
	ln -s libraries/IOToy/ IOToy
	zip -r IOToy.zip IOToy
	rm IOToy

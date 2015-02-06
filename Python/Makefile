PYTHON=`which python`
DESTDIR=/
PROJECT=iotoy

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

deb:
	debuild -uc -us

use: deb
	sudo dpkg --purge python-iotoy
	sudo dpkg -i ../python-iotoy_*.deb

clean:
	$(PYTHON) setup.py clean
	dh_clean
	rm -rf build/ MANIFEST
	find . -name '*.pyc' -delete
	rm -f ../python-iotoy_*.dsc ../python-iotoy_*.tar.gz ../python-iotoy_*.deb ../python-iotoy_*.build ../python-iotoy_*.changes


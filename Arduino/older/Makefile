

all:
	@echo "This is a basic makefile, it has two main build targets"
	@echo
	@echo "tiny - A build target to test a version of the code for Atmeta 8A also known as ATiny"
	@echo "normal - A build target for the default implementation"
	@echo

tiny:
	g++  -DTINY host_test.cpp -o tiny_host_test

normal:
	g++ host_test.cpp -o host_test

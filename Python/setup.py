#!/usr/bin/python

from distutils.core import setup
import os

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

packages = find_packages(".")
package_names = packages.keys()

if False:
    print "This is a non-ideal way of checking this."
    print "This will be dealt with better soon"
    print "For the moment this is the least bad refactor"

    import flask
    try:
        assert int(flask.__version__.split(".")[1]) > 8
    except AssertionError:
        print
        print
        print "*******************************************************"
        print
        print "  Need flask version at least 0.9, 0.10 recommended"
        print "This is so that we can return appropriate status codes!"
        print
        print "*******************************************************"
        print
        print
        raise


setup(name = "python-iotoy",
      version = "1.0.0",
      description = "python-iotoy",

      author = "Michael Sparks",
      author_email = "michael.sparks@bbc.co.uk",
      url = "http://www.rd.bbc.co.uk/~michael/",
      license ="Apache Software License",
      packages = package_names,
      package_dir = packages,

      long_description = """
This is a python package implementing an IOT Toy spike.
"""
      )

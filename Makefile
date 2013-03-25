
all:
	nosetests

release:
	python setup.py register sdist bdist_egg upload

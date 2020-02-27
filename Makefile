TESTS = $(wildcard decocare/*.py decocare/*/*.py)
test:
	python3 -m doctest -v ${TESTS}

install:
	python3 setup.py develop
	install decocare/etc/80-medtronic-carelink.rules /etc/udev/rules.d/
	udevadm control --reload-rules

ci-install:
	python3 -V
	python3 setup.py develop

ci-test: ci-install test
	# do the travis dance

docs:
	(cd doc; make)
travis: test
	# do the travis dance

.PHONY: test docs

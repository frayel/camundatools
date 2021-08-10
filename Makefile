.PHONY: build publish clean

build:
	python setup.py sdist bdist_wheel

publish:
	twine upload dist/*

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
.PHONY: test install clean

publish:
	twine upload dist/*

wheel:
	python3 setup.py bdist_wheel

install:
	pip install -r requirements.txt

clean:
	rm -rf dist
	rm -rf gpymusic.egg-info
	python3 setup.py clean --all

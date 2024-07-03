.PHONY: test dist clean upload

.DEFAULT_GOAL = test

NAME = bizcal
PY = ./env/bin/python
VER = $(shell grep version pyproject.toml | sed 's/version.*=.*"\(.*\)".*/\1/')
PKG = dist/bizcal-$(VER)-py3-none-any.whl
SRC = $(wildcard bizcal/*.py)

$(PY):
	petal make env

test: $(PY)
	$(PY) -B -m unittest test.basic

$(PKG): $(PY) $(SRC)
	$(PY) -m build --no-isolation --wheel && rm -rf $(NAME).egg-info

dist: $(PKG)

upload: $(PKG)
	$(PY) -m twine upload -r pypi $(PKG)

clean:
	rm -rf $(NAME).egg-info dist

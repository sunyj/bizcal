.PHONY: test dist clean

.DEFAULT_TARGET = test

NAME = bizcal
PY = ./env/bin/python -B

test:
	$(PY) -m unittest test.basic

dist:
	$(PY) -m build --no-isolation --wheel && rm -rf $(NAME).egg-info

clean:
	rm -rf $(NAME).egg-info dist

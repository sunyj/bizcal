.PHONY: test dist clean

.DEFAULT_GOAL = test

NAME = bizcal
PY = ./env/bin/python

$(PY):
	petal make env

test: $(PY)
	$(PY) -B -m unittest test.basic

dist: $(PY)
	$(PY) -B -m build --no-isolation --wheel && rm -rf $(NAME).egg-info

clean:
	rm -rf $(NAME).egg-info dist

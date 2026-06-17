UV_ENV=UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python
UV_RUN=$(UV_ENV) uv run --python 3.12

.PHONY: install-dev build test validate clean

install-dev:
	$(UV_RUN) python -m pip install -e .

build:
	$(UV_RUN) python scripts/build.py

test:
	$(UV_RUN) pytest -q

validate:
	$(UV_RUN) python scripts/validate_outputs.py

clean:
	rm -rf .pytest_cache .ruff_cache dist/*.tmp

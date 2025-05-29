setup_env:
	uv sync

runtest:
	. ./.venv/bin/activate && uv run pytest main.py -v --cov=main --cov-report=html

.PHONY: runtest setup_env

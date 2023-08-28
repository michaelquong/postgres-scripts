.venv:
	@python3 -m venv .venv

requirements: .venv requirements.txt
	@.venv/bin/pip install -Ur requirements.txt

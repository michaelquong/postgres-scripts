.venv:
	@python3 -m venv $@

requirements: .venv requirements.txt
	@.venv/bin/pip install -Ur $@.txt

.PHONY: image
image:
	@docker build -t mquong/scripts .

backups:
	@mkdir -p $@

.PHONY: run
run: backups
	@docker run -v "${PWD}/backups:/app/backups" -v "${PWD}/config.yaml:/app/config.yaml:ro" mquong/scripts
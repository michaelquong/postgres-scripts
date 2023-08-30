.venv:
	@python3 -m venv $@

requirements: .venv requirements.txt
	@.venv/bin/pip install -Ur $@.txt

.PHONY: image
image:
	@docker build -t my/migration .

backups:
	@mkdir -p $@

.PHONY: run
run: backups
	@docker -v ./backups:/app/backups -v ./config.yaml:/app/config.yaml:ro my/migration
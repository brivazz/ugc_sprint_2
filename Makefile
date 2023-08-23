.PHONY: install-hooks hooks remove-hooks pre-commit check

install-hooks:
	pre-commit install

update-hooks:
	pre-commit autoupdate

remove-hooks:
	pre-commit uninstall

pre-commit: install-hooks
	pre-commit run --show-diff-on-failure --color=always --all-files

check: pre-commit

.PHONY: install-hooks
install-hooks:
	pre-commit install

.PHONY: update-hooks
update-hooks:
	pre-commit autoupdate

.PHONY: remove-hooks
remove-hooks:
	pre-commit uninstall

.PHONY: pre-commit
pre-commit: install-hooks
	pre-commit run --show-diff-on-failure --color=always --all-files

.PHONY: check
check: pre-commit

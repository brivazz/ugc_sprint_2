# NENV = node_modules
# PRETTIER = $(NENV)/.bin/prettier
# DOCKERFILELINT = $(NENV)/.bin/dockerfilelint

# SHELL = /bin/bash
# .PHONY: init
# init:
# 	@echo 'Installing node version...'
# 	@. $(HOME)/.nvm/nvm.sh && nvm install

# 	@echo 'Installing node dependencies...'
# 	@npm install

# 	@echo 'Installing husky pre-commit...'
# 	@npm run prepare-husky

# .PHONY: lint
# lint:
# 	@echo 'Running prettier checks...'
# 	@$(PRETTIER) --check .

# 	@echo 'Running dockerfilelint checks...'
# 	@$(foreach dockerfile, $(wildcard src/*/Dockerfile), \
# 		$(DOCKERFILELINT) $(dockerfile) || exit 1; \
# 	)

# .PHONY: lint-fix
# lint-fix:
# 	@echo 'Running prettier auto-fixes...'
# 	@$(PRETTIER) --write .

# 	@echo 'Running dockerfilelint checks...'
# 	@$(foreach dockerfile, $(wildcard src/*/Dockerfile), \
# 		$(DOCKERFILELINT) $(dockerfile) || exit 1; \
# 	)

# .PHONY: clean
# clean:
# 	@echo 'Cleaning up node dependencies...'
# 	@rm -rf $(NENV)

# # CI-specific

# .PHONY: ci-init
# ci-init:
# 	@echo 'Installing node dependencies...'
# 	@npm install

# .PHONY: ci-login-ghcr
# ci-login-ghcr:
# 	@echo 'Logging to GitHub Container Registry...'
# 	@echo $(GITHUB_TOKEN) | docker login ghcr.io -u USERNAME --password-stdin


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
pre-commit:
    pre-commit run --show-diff-on-failure --color=always --all-files

.PHONY: check
check: pre-commit
    @pre-commit repo https://github.com/pre-commit/pre-commit-hooks rev=v4.0.0 hooks="[trailing-whitespace, end-of-file-fixer, check-yaml, check-merge-conflict, detect-private-key, debug-statements]"
    @pre-commit repo https://github.com/asottile/pyupgrade rev=v3.3.1 hooks="[pyupgrade --py311-plus]"
    @pre-commit repo https://github.com/PyCQA/isort rev=5.12.0 hooks="[isort]"
    @pre-commit repo https://github.com/psf/black rev=23.7.0 hooks="[black --exclude ^.*\\b(migrations)\\b.*$]"
    @pre-commit repo https://github.com/PyCQA/autoflake rev=v2.0.1 hooks="[autoflake]"
    @pre-commit repo https://github.com/python-jsonschema/check-jsonschema rev=0.21.0 hooks="[check-github-workflows, check-dependabot]"
    @pre-commit repo https://github.com/pre-commit/pygrep-hooks rev=v1.10.0 hooks="[python-use-type-annotations, python-check-blanket-noqa]"
    @pre-commit repo https://github.com/Yelp/detect-secrets rev=v1.4.0 hooks="[detect-secrets --args filename,.env --exclude .env.example]"

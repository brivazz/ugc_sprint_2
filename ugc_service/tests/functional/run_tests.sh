#!/usr/bin/env sh

sh -c python3 /tests/functional/utils/wait_for_api.py \
&& pytest --exitfirst /tests/functional/src

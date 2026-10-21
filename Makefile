ifndef SOURCE_FILES
	export SOURCE_FILES:=annoworkcli scripts
endif
ifndef TEST_FILES
	export TEST_FILES:=tests
endif

GITLEAKS_VERSION := v8.30.1
GITLEAKS_DOCKER_CONFIG ?= /tmp/annowork-cli-docker-config

.PHONY: init lint format test docs gitleaks generate-skill-command-index check-skill-command-index

format: generate-skill-command-index
	uv run ruff format ${SOURCE_FILES} ${TEST_FILES}
	uv run ruff check ${SOURCE_FILES} ${TEST_FILES} --fix-only --exit-zero

lint: check-skill-command-index
	uv run ruff check ${SOURCE_FILES} ${TEST_FILES}
	uv run mypy ${SOURCE_FILES} ${TEST_FILES}

generate-skill-command-index:
	uv run python scripts/generate_skill_command_index.py

check-skill-command-index:
	uv run python scripts/generate_skill_command_index.py --check

gitleaks:
	@if command -v gitleaks >/dev/null 2>&1; then \
		gitleaks git --redact --verbose .; \
	elif command -v docker >/dev/null 2>&1; then \
		mkdir -p "${GITLEAKS_DOCKER_CONFIG}"; \
		DOCKER_CONFIG="${GITLEAKS_DOCKER_CONFIG}" docker run --rm \
			-v "$$(pwd):$$(pwd)" \
			-v "$$(git rev-parse --path-format=absolute --git-common-dir):$$(git rev-parse --path-format=absolute --git-common-dir)" \
			-w "$$(pwd)" ghcr.io/gitleaks/gitleaks:${GITLEAKS_VERSION} git --redact --verbose .; \
	else \
		echo "gitleaksまたはdockerをインストールしてください。" >&2; \
		exit 127; \
	fi

test:
	uv run pytest -n auto  --cov=annoworkcli --cov-report=html tests

docs:
	cd docs && uv run make html

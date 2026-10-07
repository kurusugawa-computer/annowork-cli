ifndef SOURCE_FILES
	export SOURCE_FILES:=annoworkcli scripts
endif
ifndef TEST_FILES
	export TEST_FILES:=tests
endif



.PHONY: init lint format test docs generate-skill-command-index check-skill-command-index

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

test:
	uv run pytest -n auto  --cov=annoworkcli --cov-report=html tests

docs:
	cd docs && uv run make html

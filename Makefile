ifndef SOURCE_FILES
	export SOURCE_FILES:=annoworkcli
endif
ifndef TEST_FILES
	export TEST_FILES:=tests
endif



.PHONY: init lint format test docs

format:
	poetry run ruff format ${SOURCE_FILES} ${TEST_FILES}
	poetry run ruff check ${SOURCE_FILES} ${TEST_FILES} --fix-only --exit-zero

lint:
	poetry run ruff ${SOURCE_FILES}
	# テストコードはチェックを緩和する
	# pygrep-hooks, flake8-datetimez, line-too-long, flake8-annotations, unused-noqa
	poetry run ruff check ${TEST_FILES} --ignore PGH,DTZ,E501,ANN,RUF100
	poetry run mypy ${SOURCE_FILES} ${TEST_FILES}
	# テストコードはチェックを緩和するためpylintは実行しない
	poetry run pylint --jobs=0 ${SOURCE_FILES}

test:
	poetry run pytest -n auto  --cov=annoworkcli --cov-report=html tests

docs:
	cd docs && poetry run make html


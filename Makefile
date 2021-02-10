.PHONY: test test-debug publish

test:
	poetry run flake8 jsonrpcbase test && \
		poetry run pytest --cov=./jsonrpcbase --cov-report=html test && \
		poetry run coverage report

# For running tests while debugging your code; more verbose, inline logging
test-debug:
	poetry run flake8 jsonrpcbase test && \
		poetry run pytest --cov=./jsonrpcbase --cov-report=html -vv -x test && \
		poetry run coverage report && \
		poetry run coverage html


publish:
	poetry publish --build -vvv

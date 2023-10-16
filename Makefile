SOURCE?=yew
TESTS?=tests

lint: ## Lint source code
	@echo "🧹 Black"
	@black $(SOURCE) $(TESTS)
	@echo "🧹 Ruff"
	@ruff --fix $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@mypy --pretty $(SOURCE) $(TESTS)

test: ## Run tests
	@poetry run coverage run -m pytest $(TESTS) $(SOURCE)

test-cov-xml: ## Run tests
	@poetry run coverage run -m pytest $(TESTS) --cov $(SOURCE) --cov-report=xml

test-cov-html: ## Generate test coverage
	@poetry run coverage report --show-missing
	@poetry run coverage html

test-cov-open: test-cov-html  ## Open test coverage in browser
	@open htmlcov/index.html

SOURCE?=yew
TESTS?=tests

lint: # Lint source code
	@echo "🧹 Black"
	@black $(SOURCE) $(TESTS)
	@echo "🧹 Ruff"
	@ruff --fix $(SOURCE) $(TESTS)
	@echo "🧽 MyPy"
	@mypy --pretty $(SOURCE) $(TESTS)

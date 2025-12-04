.DEFAULT_GOAL := setup

setup:
	@echo "Setting up git hooks..."
	@echo "#!/usr/bin/env bash" > .git/hooks/pre-push
	@echo "python3 .github/workflows/util/toc-compare" >> .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "Git hook created."

	@echo "Creating dev directory..."
	@mkdir -p dev

	@echo "Creating virtual environment..."
	@python3 -m venv dev

	@echo "Installing dependencies..."
	dev/bin/python -m pip install --upgrade pip
	dev/bin/python -m pip install playwright beautifulsoup4
	dev/bin/playwright install chromium
	@echo "Setup complete."

clean:
	rm -rf dev
	rm .git/hooks/pre-push

.PHONY: setup lint

setup:
	chmod +x setup_python_project.sh
	./setup_python_project.sh

lint:
	pre-commit run --all-files

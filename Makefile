.PHONY: setup lint

PYTHON=venv/bin/python
SCRIPT=main.py
COMMAND=unsubscribe_political
CRONJOB=0 */3 * * * $(PYTHON) $(PWD)/$(SCRIPT) $(COMMAND)

lint:
	pre-commit run --all-files


check_setup:
	@echo "Checking if virtual environment is set..."
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Setting up project..."; \
		make setup; \
	else \
		echo "Virtual environment found. Proceeding..."; \
	fi

install: check_setup
	@if crontab -l 2>/dev/null | grep -q "$(COMMAND)"; then \
		echo "Already installed"; \
	else \
		( crontab -l 2>/dev/null; echo "$(CRONJOB)" ) | crontab -; \
		echo "Cron job for $(COMMAND) added."; \
	fi

uninstall: check_setup
	@if crontab -l 2>/dev/null | grep -q "$(COMMAND)"; then \
		crontab -l 2>/dev/null | grep -v "$(COMMAND)" | crontab -; \
		echo "Cron job for $(COMMAND) removed."; \
	else \
		echo "No cron job found for $(COMMAND)"; \
	fi

setup:
	chmod +x setup_python_project.sh
	./setup_python_project.sh

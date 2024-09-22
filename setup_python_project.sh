#!/bin/bash

# Function to check if pyenv is installed
install_pyenv_if_not_exist() {
  if ! command -v pyenv &> /dev/null
  then
    echo "pyenv is not installed. Installing pyenv..."
    curl https://pyenv.run | bash
    
    # Add pyenv to bashrc or zshrc based on shell
    if [ -n "$BASH_VERSION" ]; then
      echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
      echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
      echo 'eval "$(pyenv init -)"' >> ~/.bashrc
      echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
      source ~/.bashrc
    elif [ -n "$ZSH_VERSION" ]; then
      echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
      echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
      echo 'eval "$(pyenv init -)"' >> ~/.zshrc
      echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
      source ~/.zshrc
    fi
  else
    echo "pyenv is already installed."
  fi
}

# Ensure pyenv is installed
install_pyenv_if_not_exist

# Install Python 3.11.4 if not installed
if ! pyenv versions | grep -q "3.11.4"; then
  pyenv install 3.11.4
fi

# Set the local Python version to 3.11.4
pyenv local 3.11.4

# Create and activate the virtual environment
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

# Activate the virtual environment
source ./venv/bin/activate

# Install Python packages
if [ -f "requirements.txt" ]; then
  echo "Installing required Python packages..."
  pip install -r requirements.txt
else
  echo "requirements.txt file not found!"
fi

# Install pre-commit, ruff, and black
echo "Installing pre-commit, ruff, and black..."
pip install pre-commit ruff black

# Create a pre-commit config file if it doesn't exist
if [ ! -f ".pre-commit-config.yaml" ]; then
  echo "Creating .pre-commit-config.yaml..."
  cat <<EOT >> .pre-commit-config.yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.279  # Use the latest version
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 23.9.1  # Use the latest version
    hooks:
      - id: black
        language_version: python3
EOT
fi

# Install the pre-commit hooks
pre-commit install

echo "Python project setup complete. Pre-commit, ruff, and black have been installed and configured."

#!/bin/bash

# Install uv if not exists
if ! command -v uv &> /dev/null; then
    if [ -f "$HOME/.local/bin/uv" ]; then
        echo "uv found in $HOME/.local/bin"
        export PATH="$HOME/.local/bin:$PATH"
    else
        echo "uv not found. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi

# Create/Sync virtual environment
echo "Syncing dependencies with uv..."
uv sync

echo "Setup complete. To run commands, use 'uv run python src/main.py' or activate the venv with 'source .venv/bin/activate'."

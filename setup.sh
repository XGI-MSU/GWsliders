#!/bin/bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name=gwslider-env --display-name "gwslider-env"
echo "Setup complete!"
echo ""
echo "To launch the notebook, run these two commands:"
echo "  1. source .venv/bin/activate"
echo "  2. jupyter notebook"
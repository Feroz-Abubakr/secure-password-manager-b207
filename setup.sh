#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing required packages..."
pip install -r requirements.txt

echo "Setup completed."
echo "Run the project with:"
echo "source venv/bin/activate"
echo "python app.py"
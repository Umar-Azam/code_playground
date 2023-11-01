#! /usr/bin/bash

echo "Creating a virtual environment ~/.venv"

python3 -m venv ~/.venv

echo "Sourcing virtual environemnt "

source ~/.venv/bin/activate

echo "Installing setuptools"

pip install -U pip setuptools

echo "Installing poetry"

pip install poetry


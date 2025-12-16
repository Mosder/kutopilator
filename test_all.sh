#!/bin/bash

PYTHON=.venv/bin/python
for file in examples/*; do
	echo -e "\n$file";
	.venv/bin/python main.py $file;
done

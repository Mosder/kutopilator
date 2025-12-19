#!/bin/bash

PYTHON=.venv/bin/python
for file in examples/*; do
	echo -e "\n$file";
	$PYTHON main.py $file;
done

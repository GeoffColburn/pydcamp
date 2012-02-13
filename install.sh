#!/usr/bin/env bash

./setup.py install --user
./setup.py install --home ~/local
rm -r build

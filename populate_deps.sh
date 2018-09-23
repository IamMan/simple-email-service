#!/usr/bin/env bash

docker run --rm -v $(pwd)/libs/:/l sls-py-reqs-custom cp /usr/lib64/libsybdb.so.5 /l
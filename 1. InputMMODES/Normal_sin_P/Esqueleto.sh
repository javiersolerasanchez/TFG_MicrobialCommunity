#!/bin/bash

experimentos=$1

for i in $(seq 1 $experimentos); do
    python3 Simulation_NSP.py
done

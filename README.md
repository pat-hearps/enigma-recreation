# Decoding the Enigma

This project is a python emulation of the Turing Bombe, the machine developed in WW2 by Alan Turing and other codebreakers at Bletchley Park in the UK. Its purpose was to massively speed up and parallelise the brute-force component of breaking daily cyphers used by the Nazi's Enigma machines.

https://en.wikipedia.org/wiki/Bombe

## How to use

Currently just runs in local.
Requires Python >= 3.10

Create a virtual environment e.g. `python -m venv .venv`
After activating, install requirements `python -m pip install -r requirements.txt`

A basic demo can be run with a Streamlit app:

`streamlit run app.py`

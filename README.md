# BPPCode
This repository contains the code used to generate letters in Philippe Grand'Maison's master's thesis.

## Contained Projects

### GenText
Another sizable piece of the software. It is the text generation library.

### BPPGen
BPPGen uses GenText to generate recruitment letters. It also contains a small Flask server.

### BPPGenBuild
This project contains the code that built the resources for BPPGen. This project is much more flaky: it depends on such things as a 
comptatible MongoDB. All resources generated by BPPGenBuild can be found in the appropriate language's letter_data folder.

## HOWTO
### Requirements
* A Linux system.
* Python 2.7.11
* Easy install

### Install dependencies
To install in user mode, use `pip --user install`. To install in global mode, use `sudo pip install`.
#### For GenText
~~~~
pip install nltk mock
~~~~

#### For BPPGen
~~~~
pip install six certifi flask pymongo langid
~~~~

#### Test installation

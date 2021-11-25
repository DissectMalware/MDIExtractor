# MDIExtractor

Malicious Document IoC Extractor (MDIExtractor) is a collection of scripts that helps extracting IoCs from various maldoc families.

# Prerequisit

To use the scripts in this repository, you need to install [XLMMacroDeofuscator](https://github.com/DissectMalware/XLMMacroDeobfuscator)

```
pip install -U https://github.com/DissectMalware/XLMMacroDeobfuscator/archive/master.zip --force
```

# How to Use

To get URLs from Dridex instances submitted on MalwareBazaar in the last 24 hours:

```
python dridex_bazaar_tracker.py output_directory
```
To get URLs from a specific Dridex instance on your local machine:

```
python dridex_extractor.py dridex_sample.xlsb
```

# CAUTION
DO NOT RUN THESE SCRIPTS IN PRODUCTION ENVIRONMENT

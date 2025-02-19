Workflow Load testing from Postman
==================================

This directory contains some tests that have been converted from Postman to Pytest.

These tests must be run manually via the command line, or using a debugger in an IDE.

The top level pytest.ini file will skip the `load` testing directory:
```
[tool:pytest]
norecursedirs = load/*
```

Remaining issues
================
* Data upload to a workflow does not always work
* Contributors should use internal link for accessing jobs; otherwise IP Georestrictions will block.
* Minor corrections to make the testing more modular


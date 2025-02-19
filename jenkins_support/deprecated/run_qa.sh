#!/bin/bash
pytest -m "smoke" --show-capture=no --env=qa --html=./result/report.html --junitxml=./result/junit_report.xml adap/

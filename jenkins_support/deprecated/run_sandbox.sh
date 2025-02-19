#!/bin/bash
pytest --show-capture=no --env=sandbox --html=./result/report.html --junitxml=./result/junit_report.xml adap/

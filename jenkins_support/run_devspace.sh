#!/bin/bash

echo "VALUE FOR DEVSPACE_SUBDOMAIN: $DEVSPACE_SUBDOMAIN"
while [ $# -gt 0 ]; do
  case "$1" in
    --space*|-s*)
      if [[ "$1" != *=* ]]; then shift; fi # Value is next arg if no `=`
      NAMESPACE="${1#*=}"
      TEST_ENV="$NAMESPACE"."$DEVSPACE_SUBDOMAIN".devspace
      ;;
    --test-set*|-ts*)
      if [[ "$1" != *=* ]]; then shift; fi 
      TEST_SET="${1#*=}"
      # only set default MARKEREXPR if it wasn't already passed before $TEST_SET
      [[ -z "${MARKEREXPR}" ]] && MARKEREXPR=$TEST_SET
      ;;
    --file*|-f*)
      if [[ "$1" != *=* ]]; then shift; fi
      FILE="${1#*=}"
      ;;
    --marker-expr*|-m*)
      if [[ "$1" != *=* ]]; then shift; fi
      MARKEREXPR="${1#*=}"
      ;;
    --workers*|-w*)
      if [[ "$1" != *=* ]]; then shift; fi
      NUMPROCESSES="${1#*=}"
      ;;
    --flaky*|-fl*)
      INCLUDE_FLAKY='true'
      ;;
    --all-tests*|-a*)
      RUN_ALL='true'
      ;;
    --help|-h)
      echo " Possible args:"
      echo "  -s,  --space=your-devspace (required, name of devspace under test)" # Flag argument
      echo "  -ts, --test-set=mark       (required, specific pytest mark)"
      echo "  -f,  --file='./adap/subdir'    (filter tests by file or directory)"
      echo "  -m,  --marker-expr='m1 not m2' (filter tests by expression)"
      echo "  -w,  --workers=N               (default=4, 0=show debug logs)"
      echo "       --flaky     (present == true)"
      echo "       --all-tests (present == true)"
      echo "  -h,  --help      (print this message)"
      exit 0
      ;;
    *)
      >&2 printf "Error: Invalid argument\n"
      exit 1
      ;;
  esac
  shift
done

[[ -z "$TEST_ENV" ]] && echo "Missing --space=namespace arg" && exit 1
[[ -z "$TEST_SET$RUN_ALL" ]] && echo "Missing --test-set=mark or --all-tests arg" && exit 1

if [[ -f "$FILE" ]]; then
    TESTPATH=$FILE
else
	  TESTPATH='adap/'
fi

echo "First 10 lines of adap/data/account_devspace.json"
head adap/data/account_devspace.json
echo "First 10 lines of $NAMESPACE adap/data/predefined_data.json"
head adap/data/predefined_data.json
echo "qa_secret.key"
cat qa_secret.key
echo
echo "!!!!!!! Starting pytest run against devspace $NAMESPACE with ${NUMPROCESSES:-4} worker threads"

if [[ $RUN_ALL = 'true' ]]; then
  echo " Running all tests"
  pytest --numprocesses=${NUMPROCESSES:-4} \
         --show-capture=${SHOWCAPTURE:-no} \
         --capture=${CAPTURE:-no} \
         --env=$TEST_ENV \
         --flaky=${INCLUDE_FLAKY:-false}  \
         --html=./result/report.html \
         --junitxml=./result/junit_report.xml  \
         --alluredir=allure_result_folder  \
         $TESTPATH
else
  echo " Running $TESTPATH tests in set '$TEST_SET' marked '${MARKEREXPR}'"
  pytest  -m "${MARKEREXPR}" \
          --numprocesses=${NUMPROCESSES:-4} \
          --show-capture=${SHOWCAPTURE:-no} \
          --capture=${CAPTURE:-no} \
          --env=$TEST_ENV \
          --set="$TEST_SET" \
          --flaky=${INCLUDE_FLAKY:-false}  \
          --html=./result/report.html \
          --junitxml=./result/junit_report.xml  \
          --alluredir=allure_result_folder  \
          $TESTPATH
fi

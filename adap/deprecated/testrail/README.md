[//]: # (The script is created for migrating test cases from Spira to Testrail via API .)

[//]: # (How to run:)

[//]: # (1. By proving args: -testrail_project_id - project_id in testrail, )

[//]: # (-testrail_suite_id - the id of suite in Testrail where the test cases will)

[//]: # (migrate, --spira_section_ids - here count all section ids that contain)

[//]: # (test cases which will be migrate)

[//]: # (```python3 migrate_to_test_rail.py  -testrail_project_id=2 -testrail_suite_id=21 -spira_section_ids 120 131 132```)
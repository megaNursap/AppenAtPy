The script is created for cleaning up platform_performance DB to speed up Grafana dashboard usage.
How to run:
1. By proving a count of sessions which should be deleted by ordering from older to newest  
``` python3 main.py 3``` - will be running the script and delete 3 sessions across all tables ordering from older to newest
2. By proving a range of session ids which should be deleted inclusively  
``` python3 main.py 3-10``` - will be running the script and delete [3, 4, 5, 6, 7, 8, 9, 10] session ids across all tables


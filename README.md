# jira-transitions.py
## Getting JIRA transition times
Given a JIRA query the script will look up and calculate the total time in hours for every transition status for all tickets that is returned by the filter query. 

Make sure you have access results to the filter query before executing this script.

## How to Run
First you need to generate a Personal Access Token in Jira.

Then execute the following script.
```
$ python jira-transitions.py -f <output-filename> -q <JIRA-filter-query>
```

Running the script will give you an output text file list of issues with the calculated transition time.

```
TCKT-6438
"Open" = 4.72 hours,"In Progress" = 22.56 hours,"In QA Progress" = 91.99 hours,"In Review" = 180.63 hours,"Reopened" = 20.70 hours,

TCKT-6400
"Open" = 4.72 hours,"In Progress" = 22.56 hours,"In QA Progress" = 91.99 hours,"In Review" = 180.63 hours,"Reopened" = 20.70 hours
```


## Dependencies
```
$ pip install jira
```
KBP
===

[TAC KBP competition](http://www.nist.gov/tac/2014/KBP/)

The following files in the kbp/ directory will be useful for running the application:
- env.sh: sets up environment variables
- setup_database.sh: loads the starting DB and creates additional necessary tables
- run.sh: runs the application using DeepDive

Edit setup_database.sh as necessary to change the PGHOST, PGPORT, and DBNAME variables.



If running the KBP application for the first time, first set up the database and environment variables:
```
>> source env.sh
>> source setup_database.sh
```

To run DeepDive (only this setp needs to re-run during development):
```
>> ./run.sh
```
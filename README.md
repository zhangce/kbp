KBP
===

[TAC KBP competition](http://www.nist.gov/tac/2014/KBP/)

The following files in the kbp/ directory will be useful for running the application:
- env.sh: sets up DeepDive environment variables
- env_db.sh: sets up DB-specific environment variables
- setup_database.sh: loads the starting DB and creates additional necessary tables
- run.sh: runs the application using DeepDive

Edit env_db.sh as necessary to change the PGHOST, PGPORT, and DBNAME variables.

If running the KBP application for the first time, first set up the database - this also runs both env.sh and env_db.sh:
```
>> source setup_database.sh
```

To run DeepDive (only this step needs to be re-run during development) - this also runs both env.sh and env_db.sh:
```
>> ./run.sh
```
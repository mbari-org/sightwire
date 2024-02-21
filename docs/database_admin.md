# Database Admin

This document provides a set of recipes for common database admin tasks.

# Setup
See the [README](../README.md) document for instructions on setting up the environment.
See the [database setup](database_setup.md) document for instructions on database setup.
The assumption here is that your environment is setup and the database is running.
For data loading tasks, a TATOR_TOKEN and TATOR_HOST environment variable should be set.
 
# Login and Registration

## Login to the web application
Be patient. The first time the docker compose stack is started, 
it will take a few minutes to load.  

Open a web browser 
http://localhost:8080/accounts/login/?next=/projects/

## Register a new user
New users register at
http://localhost:8080/registration

**Important** The admin user must add new user to the 902204-CoMPAS project before they 
can see the project


#  Backups

### Reset the database
Caution - this will delete all data in the database!!  This is the fastest
way to drop all data when experimenting. Proceed with caution.

```shell
python sightwire database init
```

### Backup the database
This will create a backup of the database in the backup directory
specified in the .env file DATA_DIR, e.g. /home/ops/data/backup.  This only makes
a backup of the database, not the thumbnail images.

```shell
cd tator && make backup
```
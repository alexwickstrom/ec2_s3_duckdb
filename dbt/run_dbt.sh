#!/bin/bash
# run_dbt.sh

# Set the DBT_PROFILES_DIR environment variable to the current directory's 'dbt' folder
export DBT_PROFILES_DIR=$(pwd)

# Now run dbt with all the arguments passed to the script
dbt "$@"
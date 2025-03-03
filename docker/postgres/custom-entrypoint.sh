#!/bin/bash
set -e

# First, run our permission fix script to ensure PostgreSQL has the correct file permissions.
# This is crucial to avoid "PermissionError: [Errno 13] Permission denied" errors
# (e.g., when running pytest) caused by improper ownership or permissions on PostgreSQL data files.

# Fix permissions for PostgreSQL data directory to ensure the database can read/write
/usr/local/bin/fix_permissions.sh

# Then, execute the original PostgreSQL entrypoint with all arguments
exec docker-entrypoint.sh "$@"
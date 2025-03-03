#!/bin/bash
echo "Starting permission fix script at $(date)" > /tmp/fix_permissions.log

# Use the PostgreSQL data directory (PGDATA) which is configurable
PGDATA=${PGDATA:-/var/lib/postgresql/data}

# Set permissions and handle errors
if [ -d "$PGDATA" ]; then
  echo "Setting permissions for $PGDATA" >> /tmp/fix_permissions.log
  
  # targeted permissions - only what PostgreSQL needs
  find "$PGDATA" -type d -exec chmod 700 {} \;
  find "$PGDATA" -type f -exec chmod 600 {} \;
  chown -R postgres:postgres "$PGDATA"
    
  echo "Permissions fixed successfully for $PGDATA" >> /tmp/fix_permissions.log
else
  echo "Directory $PGDATA does not exist yet. Will be created by PostgreSQL." >> /tmp/fix_permissions.log
fi
FROM postgres:latest

# Copy the SQL script to initialize databases and the permission fix script
COPY ./docker/postgres/create_databases.sql /docker-entrypoint-initdb.d/02_create_databases.sql
COPY ./docker/postgres/fix_permissions.sh /usr/local/bin/fix_permissions.sh
COPY ./docker/postgres/custom-entrypoint.sh /usr/local/bin/custom-entrypoint.sh

# Make scripts executable
RUN chmod +x /usr/local/bin/fix_permissions.sh /usr/local/bin/custom-entrypoint.sh

# Set the custom entrypoint to use our permission fix script before starting PostgreSQL
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["postgres"]
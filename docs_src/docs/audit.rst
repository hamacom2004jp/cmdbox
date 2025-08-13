.. -*- coding: utf-8 -*-

****************************************************
Audit Log
****************************************************

This document explains how to use the audit log functionality in `cmdbox`. The audit log provides commands to create, delete, search, and write audit logs.

Overview
========

The audit log functionality is implemented using the following modules:

- `cmdbox.app.features.cli.cmdbox_audit_createdb`: Create a database for audit logs.
- `cmdbox.app.features.cli.cmdbox_audit_delete`: Delete audit logs based on specific conditions.
- `cmdbox.app.features.cli.cmdbox_audit_search`: Search audit logs with various filters.
- `cmdbox.app.features.cli.cmdbox_audit_write`: Write new audit logs.

Each command is executed using the `cmdbox` CLI with the `-m audit` mode and the corresponding `-c` command.

Commands
========

1. **Create Audit Database**

   Use the `createdb` command to initialize a database for storing audit logs.

   Example:
   ```
   cmdbox -m audit -c createdb --pg_host localhost --pg_port 5432 --pg_user postgres --pg_password password --pg_dbname audit
   ```

   Options:
   - `--pg_host`: PostgreSQL host.
   - `--pg_port`: PostgreSQL port.
   - `--pg_user`: PostgreSQL user name.
   - `--pg_password`: PostgreSQL password.
   - `--pg_dbname`: PostgreSQL database name.

2. **Delete Audit Logs**

   Use the `delete` command to remove audit logs based on specific conditions.

   Example:
   ```
   cmdbox -m audit -c delete --delete_audit_type user_action --delete_clmsg_user admin
   ```

   Options:
   - `--delete_audit_type`: Type of audit to delete.
   - `--delete_clmsg_user`: User who generated the message.

3. **Search Audit Logs**

   Use the `search` command to retrieve audit logs with filters.

   Example:
   ```
   cmdbox -m audit -c search --filter_audit_type user_action --filter_clmsg_user admin --limit 10
   ```

   Options:
   - `--filter_audit_type`: Type of audit to filter.
   - `--filter_clmsg_user`: User who generated the message.
   - `--limit`: Number of rows to retrieve.

4. **Write Audit Logs**

   Use the `write` command to record a new audit log.

   Example:
   ```
   cmdbox -m audit -c write --audit_type user_action --clmsg_user admin --clmsg_title "User Login" --clmsg_body '{"status": "success"}'
   ```

   Options:
   - `--audit_type`: Type of audit.
   - `--clmsg_user`: User who generated the message.
   - `--clmsg_title`: Title of the message.
   - `--clmsg_body`: Body of the message in JSON format.

Advanced Usage
==============

**Using PostgreSQL for Audit Logs**

To enable PostgreSQL for audit logs, specify the `--pg_enabled` option without any value and provide the necessary PostgreSQL connection details.

Example:
```
cmdbox -m audit -c write --pg_enabled --pg_host localhost --pg_port 5432 --pg_user postgres --pg_password password --pg_dbname audit --audit_type system_event --clmsg_title "System Update"
```

**Retention Period**

The `--retention_period_days` option allows you to specify how long audit logs should be retained. If set to `0` or less, logs will be kept indefinitely.

Example:
```
cmdbox -m audit -c write --retention_period_days 365 --audit_type user_action --clmsg_user admin --clmsg_title "Data Export"
```

# profile_app_stack

Deploys and manages a Python application with a systemd service, virtual environment, database integration, log rotation, backups, health checks, and optional production monitoring.

## Credentials

Provide `db_password` and `secret_key` through the configured AAP credential types. Secret-bearing tasks use `profile_app_stack_secure_logging`, which defaults to `true`.

## Main variables

- `app_stack_app_name`
- `app_stack_app_repo`
- `app_stack_app_revision`
- `app_stack_app_dir`
- `app_stack_app_port`
- `app_stack_db_host`
- `app_stack_db_name`
- `app_stack_db_user`
- `app_stack_worker_count`
- `app_stack_environment`

Production and staging overrides are supplied through their respective group variable files.

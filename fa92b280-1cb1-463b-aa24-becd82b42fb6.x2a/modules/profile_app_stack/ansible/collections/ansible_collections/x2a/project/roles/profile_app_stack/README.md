# profile_app_stack

Deploys and manages the `test-app` Python application stack.

The role installs Python and build dependencies, creates the application account,
checks out the configured Git repository, creates a virtual environment, installs
requirements, renders the protected environment file, manages the systemd service,
and configures scheduled database backups and health checks.

Database credentials and the application secret key are supplied by AAP credential
variables (`db_host`, `db_port`, `db_name`, `db_user`, `db_password`, and `secret_key`).
Tasks handling secret values use `profile_app_stack_secure_logging`.

## Example

```yaml
- hosts: app_servers
  become: true
  roles:
    - x2a.project.profile_app_stack
```

Set `profile_app_stack_environment` to `production` to enable Prometheus exporter,
pushgateway, and application metrics scheduling.

# profile_app_stack

Deploys a Python application from Git with a virtual environment, PostgreSQL integration, systemd service, log rotation, backups, health checks, and optional production Prometheus monitoring.

## Requirements

- Linux host with privilege escalation.
- AAP credential variables `db_host`, `db_port`, `db_name`, `db_user`, `db_password`, and `secret_key`.
- PostgreSQL command-line tooling for local database provisioning.

## Usage

```yaml
- name: Deploy application stack
  hosts: app_servers
  become: true
  roles:
    - x2a.project.profile_app_stack
```

Set role defaults to customize the repository, application paths, service settings, and environment. Secret values are supplied by AAP credentials and are not stored in role defaults.

## Idempotency

Tasks are designed to be idempotent. Repository updates, package installation, virtual environment setup, configuration rendering, service activation, and cron management converge safely.

## License

Apache-2.0

## Author

Platform Team

# chef_flpath_4648_credentials

<!-- FLPATH-3351-TC-07-RULE -->

This role creates a configuration file containing API endpoint information and credentials.

## Requirements

- Ansible 2.9 or higher
- Root privileges for file creation with secure permissions

## Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| endpoint | string | https://example.test/api | API endpoint URL |
| username | string | fixture-user | API username for authentication |
| api_token | string | none (required) | API authentication token (injected by AAP credential type) |
| chef_flpath_4648_credentials_secure_logging | boolean | true | Whether to enable secure logging for sensitive variables |

## Dependencies

None

## Example Playbook

```yaml
---
- name: Configure API credentials
  hosts: all
  become: true
  roles:
    - role: x2a.project.chef_flpath_4648_credentials
```

## License

Apache-2.0

## Author Information

Migrated from Chef cookbook
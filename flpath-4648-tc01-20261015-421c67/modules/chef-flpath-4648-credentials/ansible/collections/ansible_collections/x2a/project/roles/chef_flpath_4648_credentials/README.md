# chef_flpath_4648_credentials

FLPATH-3351-TC-07-RULE

This role manages a credentials configuration file for API access.

## Requirements

- Ansible 2.9 or higher

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| endpoint | https://example.test/api | API endpoint URL |
| username | fixture-user | Username for API authentication |
| api_token | - | API token for authentication (required, injected via AAP credential) |
| chef_flpath_4648_credentials_secure_logging | true | Controls whether tasks with sensitive variables log their output |

## Dependencies

None

## Example Playbook

```yaml
---
- hosts: all
  roles:
    - role: x2a.project.chef_flpath_4648_credentials
```

## License

Apache-2.0
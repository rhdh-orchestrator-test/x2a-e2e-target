# flpath_4648_types

FLPATH-3351-TC-07-RULE

## Description

This role manages configuration files and directories for the argument-specs-fixture application.
It creates the application's base directory and configuration file, as well as separate configuration
files for each configured site.

## Requirements

- Ansible 2.9 or higher

## Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| flpath_4648_types_app_name | string | 'argument-specs-fixture' | Name of the application being configured |
| flpath_4648_types_enabled | boolean | true | Whether the application is enabled |
| flpath_4648_types_port | integer | 8080 | TCP port the application listens on |
| flpath_4648_types_ratio | float | 1.5 | Floating point ratio value for application configuration |
| flpath_4648_types_allowed_hosts | list | ['localhost', 'example.test'] | List of hosts allowed to connect to the application |
| flpath_4648_types_config | dict | {timeout: 30, retries: 3} | Dictionary of additional configuration parameters |
| flpath_4648_types_sites | dict | See below | Dictionary of site configurations keyed by site name |

### Default Sites Configuration

```yaml
flpath_4648_types_sites:
  test.example.test:
    document_root: '/srv/test'
    ssl_enabled: true
  ci.example.test:
    document_root: '/srv/ci'
    ssl_enabled: false
```

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: x2a.project.flpath_4648_types
      vars:
        flpath_4648_types_port: 8888
        flpath_4648_types_sites:
          prod.example.com:
            document_root: '/srv/prod'
            ssl_enabled: true
```

## License

Apache-2.0

## Author Information

X2Ansible Team
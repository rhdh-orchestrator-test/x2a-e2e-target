# chef_flpath_4648_vars

FLPATH-3351-TC-07-RULE

This role configures a simple configuration file for a service named 'fixture-service'. It creates a file at `/etc/flpath-4648-vars.conf` with a service name parameter.

## Requirements

None

## Role Variables

Available variables are listed below, along with their default values:

```yaml
# Name of the service to be configured
chef_flpath_4648_vars_service_name: 'fixture-service'
```

## Dependencies

None

## Example Playbook

```yaml
---
- hosts: servers
  roles:
    - role: x2a.project.chef_flpath_4648_vars
      vars:
        chef_flpath_4648_vars_service_name: 'my-custom-service'
```

## License

Apache-2.0

## Author Information

This role was created as part of a Chef to Ansible migration project.
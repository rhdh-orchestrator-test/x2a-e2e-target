# x2a.project chef_flpath_4648_types Role

This role manages configuration for the application specified by `chef_flpath_4648_types_app_name`.

## Requirements

This role assumes:
1. The parent directory `/srv` already exists, or appropriate permissions are available to create it.
2. The application referenced by `chef_flpath_4648_types_app_name` is already installed on the target system. This role only manages its configuration, not the installation of the application itself.

## Role Variables

All variables for this role are defined with appropriate types in the role's argument_specs.yml:

- `chef_flpath_4648_types_app_name`: Name of the application (string)
- `chef_flpath_4648_types_enabled`: Whether the application is enabled (boolean)
- `chef_flpath_4648_types_port`: TCP port the application listens on (integer)
- `chef_flpath_4648_types_ratio`: Ratio configuration for the application (float)
- `chef_flpath_4648_types_allowed_hosts`: List of hosts allowed to connect to the application (list of strings)
- `chef_flpath_4648_types_config`: Application configuration parameters (dictionary)
- `chef_flpath_4648_types_sites`: Site configuration dictionary (nested dictionary)

## Dependencies

No external dependencies.

## Example Playbook

Including an example of how to use your role:

```yaml
- name: Execute tasks on servers
  hosts: servers
  roles:
    - role: x2a.project.chef_flpath_4648_types
      chef_flpath_4648_types_app_name: "myapp"
      chef_flpath_4648_types_port: 9090
```

Another way to consume this role would be:

```yaml
- name: Initialize the chef_flpath_4648_types role from x2a.project
  hosts: servers
  gather_facts: false
  tasks:
    - name: Trigger invocation of chef_flpath_4648_types role
      ansible.builtin.include_role:
        name: x2a.project.chef_flpath_4648_types
      vars:
        chef_flpath_4648_types_port: 9090
```

## Role Idempotency

This role is idempotent (True)

## Role Atomicity

This role is atomic (True)

## Roll-back capabilities

The configuration files are backed up before modification (with backup: true option), allowing for manual rollback if needed.

## Argument Specification

This role includes a complete argument_specs.yml that validates all arguments provided to the role.

## License

Apache-2.0

## Author Information

Maintained by the x2a team.

# FLPATH-3351-TC-07-RULE
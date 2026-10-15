# chef_flpath_4648_types

<!-- FLPATH-3351-TC-07-RULE -->

This role creates application directory and configuration file with different data types.

## Role Variables

| Variable                             | Type    | Default Value            | Description                              |
|--------------------------------------|---------|--------------------------|------------------------------------------|
| chef_flpath_4648_types_app_name      | string  | 'argument-specs-fixture' | Name of the application                  |
| chef_flpath_4648_types_enabled       | boolean | true                     | Whether the application is enabled       |
| chef_flpath_4648_types_port          | integer | 8080                     | Port the application listens on          |
| chef_flpath_4648_types_ratio         | float   | 1.5                      | Ratio value used by the application      |
| chef_flpath_4648_types_allowed_hosts | list    | ['localhost', 'example.test'] | List of allowed hosts               |
| chef_flpath_4648_types_config        | dict    | {timeout: 30, retries: 3} | Configuration parameters                |

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: x2a.project.chef_flpath_4648_types
      vars:
        chef_flpath_4648_types_port: 9000
        chef_flpath_4648_types_config:
          timeout: 60
          retries: 5
```

## License

Apache-2.0
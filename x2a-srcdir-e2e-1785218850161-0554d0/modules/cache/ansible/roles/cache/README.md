# Cache Role

This role installs and configures Redis server as a caching solution.

## Requirements

- Ansible 2.9 or higher

## Role Variables

See `defaults/main.yml` for all available variables.

## Dependencies

- eloy.redis collection

## Example Playbook

```yaml
- hosts: cache_servers
  roles:
    - role: cache
```
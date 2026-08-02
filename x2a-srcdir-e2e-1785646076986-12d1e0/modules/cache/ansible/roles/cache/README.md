# Cache Role

This role installs and configures Redis server as a simple caching solution.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values:

```yaml
redis_package_name: redis-server
redis_service_name: redis-server
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: cache
```

## License

Apache-2.0
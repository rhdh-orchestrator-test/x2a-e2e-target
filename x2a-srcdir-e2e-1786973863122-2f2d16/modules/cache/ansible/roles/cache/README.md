# Cache Role

This role installs and configures Redis server as a simple cache.

## Requirements

None.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| redis_package_name | redis-server | Name of the Redis package to install |
| redis_service_name | redis-server | Name of the Redis service to manage |

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
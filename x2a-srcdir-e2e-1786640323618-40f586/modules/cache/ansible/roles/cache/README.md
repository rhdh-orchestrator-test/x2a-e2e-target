# Cache Role

This role installs and configures Redis server as a simple cache.

## Requirements

None.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| redis_server_package | redis-server | Redis server package name |
| redis_server_service | redis-server | Redis server service name |
| redis_port | 6379 | Redis default port |
| redis_bind_address | 127.0.0.1 | Redis default bind address |

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
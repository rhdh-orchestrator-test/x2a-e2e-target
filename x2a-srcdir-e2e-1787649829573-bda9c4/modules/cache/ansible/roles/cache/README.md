# Cache Role

This role installs and configures Redis server as a caching solution.

## Requirements

- Ansible 2.9 or higher
- Ubuntu 18.04+ or CentOS/RHEL 7+

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Redis server package name
cache_redis_package: redis-server

# Redis server service name
cache_redis_service: redis-server

# Whether to enable the Redis service
cache_redis_enabled: true

# Redis service state (started, stopped)
cache_redis_state: started

# Redis default port
cache_redis_port: 6379

# Redis default bind address
cache_redis_bind: 127.0.0.1
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: cache_servers
  roles:
    - role: cache
      vars:
        cache_redis_bind: 0.0.0.0  # Allow external connections
```

## License

Apache-2.0

## Author Information

Originally created for Chef Example.
Converted to Ansible role format.
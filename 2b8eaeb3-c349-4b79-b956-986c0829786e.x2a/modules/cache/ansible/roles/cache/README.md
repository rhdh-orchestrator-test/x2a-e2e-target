# Redis Role

This role installs and configures Redis, an open source, in-memory data structure store, used as a database, cache, and message broker.

## Requirements

- Ansible 2.9 or higher
- Ubuntu 18.04+, Debian 9+, or RHEL/CentOS 7+

## Role Variables

### Installation Options

```yaml
# Installation method (package or source)
redis_package_install: true

# Redis version (only used for source installation)
redis_version: "6.2.6"
redis_source_url: "http://download.redis.io/releases/redis-{{ redis_version }}.tar.gz"
redis_install_dir: "/usr/local"

# User/group settings
redis_user: "redis"
redis_group: "redis"
```

### System Settings

```yaml
# System limits
redis_set_limits: true
redis_nofile_limit: 65536

# OS default Redis service
redis_disable_os_default: true
```

### Redis Instance Configuration

```yaml
redis_instances:
  - port: 6379
    name: "6379"
    datadir: "/var/lib/redis/6379"
    logdir: "/var/log/redis"
    loglevel: "notice"
    # ... additional Redis configuration options
```

## Example Playbook

```yaml
- hosts: redis_servers
  roles:
    - role: cache
      vars:
        redis_instances:
          - port: 6379
            maxmemory: "512mb"
            maxmemory_policy: "allkeys-lru"
          - port: 6380
            maxmemory: "256mb"
            maxmemory_policy: "volatile-lru"
```

## License

MIT

## Author Information

Ansible Migration Team
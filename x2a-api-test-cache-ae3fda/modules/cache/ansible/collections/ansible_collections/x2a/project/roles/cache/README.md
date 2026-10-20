# Ansible Role: cache

## Description

This role installs and configures Redis and Memcached caching services. It deploys:
- **Redis** on port 6379 with password authentication
- **Memcached** on port 11211

The role creates necessary directories, deploys configuration files, and manages service lifecycle.

## Requirements

- Ansible 2.9 or higher
- Target systems: Ubuntu (20.04, 22.04) or RHEL/CentOS (8, 9)
- ansible.posix collection (>= 1.5.0)

## Role Variables

### Redis Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cache_redis_port` | `6379` | TCP port for Redis server |
| `cache_redis_bind` | `127.0.0.1` | IP address Redis should bind to |
| `cache_redis_maxmemory` | `256mb` | Maximum memory Redis can use |
| `cache_redis_maxmemory_policy` | `allkeys-lru` | Redis eviction policy when maxmemory is reached |
| `cache_redis_log_dir` | `/var/log/redis` | Directory for Redis log files |
| `cache_redis_config_file` | `/etc/redis/6379.conf` | Path to Redis configuration file |
| `cache_redis_data_dir` | `/var/lib/redis/6379` | Directory for Redis data persistence |
| `cache_redis_user` | `redis` | System user for Redis service |
| `cache_redis_group` | `redis` | System group for Redis service |
| `cache_redis_service_name` | `redis` | Name of the Redis systemd service |

### Memcached Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cache_memcached_memory` | `64` | Memory limit for Memcached in megabytes |
| `cache_memcached_port` | `11211` | TCP port for Memcached server |
| `cache_memcached_listen` | `127.0.0.1` | IP address Memcached should bind to |
| `cache_memcached_maxconn` | `1024` | Maximum number of simultaneous connections |
| `cache_memcached_user` | `memcache` | System user for Memcached service |
| `cache_memcached_service_name` | `memcached` | Name of the Memcached systemd service |

### Security

| Variable | Default | Description |
|----------|---------|-------------|
| `cache_secure_logging` | `true` | Whether to hide sensitive credential data in logs |

### AAP Credential Variables

The following credential variables are injected by AAP credential types at runtime:

| Variable | Required | Description |
|----------|----------|-------------|
| `redis_password` | Yes | Redis authentication password |

## Dependencies

This role requires the `ansible.posix` collection. Install it using:

```bash
ansible-galaxy collection install -r requirements.yml
```

## Example Playbook

```yaml
---
- name: Configure cache services
  hosts: cache_servers
  become: true
  roles:
    - role: x2a.project.cache
      vars:
        cache_redis_bind: 0.0.0.0
        cache_redis_maxmemory: 512mb
        cache_memcached_memory: 128
```

## Usage with AAP

When using this role with Ansible Automation Platform:

1. Create a custom credential type for Redis authentication (see `aap-configuration/controller_credential_types.yml`)
2. Create a credential using that type with the Redis password
3. Attach the credential to your job template
4. The `redis_password` variable will be automatically injected at runtime

## Verification

After running the role, verify the services:

### Redis

```bash
# Check service status
systemctl status redis

# Test Redis connectivity with authentication
redis-cli -p 6379 -a "${redis_password}" PING

# Verify configuration
redis-cli -p 6379 -a "${redis_password}" CONFIG GET requirepass
```

### Memcached

```bash
# Check service status
systemctl status memcached

# Test Memcached connectivity
echo "version" | nc localhost 11211

# Check memory stats
echo "stats" | nc localhost 11211 | grep bytes
```

## Directory Structure

```
cache/
├── README.md
├── meta/
│   ├── main.yml
│   └── argument_specs.yml
├── defaults/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   └── validate_credentials.yml
├── templates/
│   ├── redis.conf.j2
│   ├── memcached.conf.j2
│   └── memcached.sysconfig.j2
├── handlers/
│   └── main.yml
├── requirements.yml
└── aap-configuration/
    ├── controller_credential_types.yml
    └── controller_credentials.yml
```

## License

Apache-2.0

## Author Information

This role was migrated from Chef cookbook to Ansible as part of the x2a infrastructure automation initiative.

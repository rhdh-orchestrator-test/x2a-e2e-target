# cache

Installs and configures Memcached and a standalone Redis instance for cache workloads.

## Credentials

Provide `redis_password` through an AAP credential type or Ansible Vault. The role validates
this credential before configuration and suppresses secret-bearing task output by default.

## Key variables

- `cache_memcached_memory`: Memcached memory in MB (default `64`).
- `cache_memcached_port`: Memcached TCP port (default `11211`).
- `cache_redis_port`: Redis TCP port (default `6379`).
- `cache_secure_logging`: Hide Redis credential task output (default `true`).

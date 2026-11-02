# profile_redis_cluster

Configures the standalone Redis instance described by the Puppet profile through the `eloy.redis.redis` Private Hub collection.

## Defaults

- Port: `6379`
- Bind address: `0.0.0.0`
- Maximum memory: `256mb`
- AOF persistence: enabled with `everysec`
- RDB persistence: enabled
- Redis Cluster, Sentinel, and replication: disabled

The Redis password is supplied by the AAP credential variable `redis_password` and should not be committed to source control.

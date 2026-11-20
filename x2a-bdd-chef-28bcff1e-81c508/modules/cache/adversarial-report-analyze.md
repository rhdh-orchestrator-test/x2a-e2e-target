

## Adversarial Review Findings

**Agent:** qe-checklist-auditor

**Summary:** The migration plan is materially incomplete and exposes security-sensitive details. It incorrectly claims Redis implementation artifacts are unavailable, omits relevant Redis and Memcached source files, embeds a plaintext Redis password, fails to require network restrictions for Redis and Memcached, omits Memcached systemd hardening, and does not specify secure Redis configuration-file ownership and permissions.

### [CRITICAL] migration-plan-cache.md:29, 56–70, 93–99, 125–131

Redis implementation details are incorrectly reported as unavailable.

**Evidence:**
```
The plan says the Redis package, provider implementation, configuration template, and service resource are unavailable and that no templates are rendered. The workspace contains redisio resources/server.rb, resources/configure.rb, and templates/default/redis.conf.erb. server.rb creates and enables the service at lines 338–362, renders /etc/redis/<instance>.conf at lines 230–330, and configure.rb defines package/configuration behavior at lines 36–153. The plan may therefore omit service-unit construction, configuration paths, runtime/data directories, persistence, security settings, and template defaults.
```

### [CRITICAL] migration-plan-cache.md:33–43, 58–70

The analyzed-file inventory is incomplete.

**Evidence:**
```
The inventory omits Redis resources/configure.rb, resources/server.rb, resources/install.rb, resources/_partial/_server.rb, and templates/default/redis.conf.erb. It also omits Memcached resources/memcached_instance.rb and libraries/helpers.rb, which define generated systemd units, hardening, package installation, service naming, CLI arguments, paths, and configuration rendering.
```

### [CRITICAL] migration-plan-cache.md:26, 91, 148–154, 262–263

A plaintext Redis password is exposed repeatedly in the migration plan and validation commands.

**Evidence:**
```
The plan includes `redis_secure_password_123` in the service summary and module explanation and passes it directly to redis-cli with `-a`. The source also contains the hardcoded secret at cache/recipes/default.rb:8. This exposes the credential through committed artifacts, shell history, process listings, CI logs, or command auditing.
```

### [WARNING] migration-plan-cache.md:23–29, 168–173, 233–280

Redis may be exposed on all interfaces without an explicit network restriction.

**Evidence:**
```
The plan documents port 6379 but does not identify or require a bind address. The Redis template emits no bind directive when unset at templates/default/redis.conf.erb:50–52, and the source supplies no address or protected-mode setting at cache/recipes/default.rb:5–14. The template states Redis listens on all available interfaces by default. Redis has a password but no TLS, and the plan lacks firewall or private-interface requirements.
```

### [WARNING] migration-plan-cache.md:18, 168–173, 224–231

Memcached is configured as unauthenticated TCP and UDP on all interfaces, but the exposure risk and controls are not documented.

**Evidence:**
```
The plan specifies listen address 0.0.0.0 and TCP and UDP port 11211. memcached/libraries/helpers.rb:58–64 constructs the command with `-U <udp_port> -p <port> -l <listen>`. There is no authentication, and unrestricted UDP can enable abuse or amplification if reachable beyond a trusted network.
```

### [WARNING] migration-plan-cache.md:103–119

Important Memcached systemd hardening and restart behavior are not captured.

**Evidence:**
```
memcached/resources/memcached_instance.rb:104–130 creates a unit with PrivateTmp=true, ProtectSystem=full, NoNewPrivileges=true, PrivateDevices=true, CapabilityBoundingSet=CAP_SETGID CAP_SETUID CAP_SYS_RESOURCE, RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX, and Restart=on-failure. The plan summarizes package, ports, directories, and service state but omits these directives, LimitNOFILE, service user, and command-line requirements.
```

### [WARNING] migration-plan-cache.md:23–29, 282–298

Redis configuration-file ownership, permissions, and secret handling are insufficiently specified.

**Evidence:**
```
The plan only says to render the password-bearing configuration with restrictive permissions and validates with stat without an expected result. redisio/resources/server.rb:230–235 sets owner, group, and mode from resolved values and new_resource.permissions, whose default must be derived from the resource partial. Without an explicit target, Ansible could create a world-readable /etc/redis/6379.conf.
```

---
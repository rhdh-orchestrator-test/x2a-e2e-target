---
source-path: fixtures/chef-flpath-4648-types
---

# Migration Plan: chef-flpath-4648-types

**TLDR**: This cookbook configures a simple application service with two website instances. It creates a main configuration file with various settings and sets up document roots and configuration files for two websites, each with different SSL settings.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.example.test**: Website instance with SSL enabled
  - Location/Path: /srv/test (document root)
  - Key Config: SSL enabled (true)
  - Config File: /etc/test.example.test.conf

- **ci.example.test**: Website instance without SSL
  - Location/Path: /srv/ci (document root)
  - Key Config: SSL disabled (false)
  - Config File: /etc/ci.example.test.conf

## File Structure

```
fixtures/chef-flpath-4648-types/recipes/default.rb
fixtures/chef-flpath-4648-types/attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`fixtures/chef-flpath-4648-types/recipes/default.rb`):
   - Creates main application configuration file at /etc/argument-specs-fixture.conf
     - Contains settings: enabled=true, port=8080, ratio=1.5, hosts=localhost,example.test, timeout=30, retries=3
   - Resources: file (1)
   
   - For site: test.example.test
     - Creates document root directory: /srv/test
     - Creates configuration file: /etc/test.example.test.conf with ssl_enabled=true
     - Resources: directory (1), file (1)
   - For site: ci.example.test
     - Creates document root directory: /srv/ci
     - Creates configuration file: /etc/ci.example.test.conf with ssl_enabled=false
     - Resources: directory (1), file (1)

## Dependencies

**External cookbook dependencies**: None detected
**System package dependencies**: None detected
**Service dependencies**: None detected

## Credentials

**Detection Summary**: 0 credentials detected

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/argument-specs-fixture.conf
- /etc/test.example.test.conf
- /etc/ci.example.test.conf
- /srv/test (directory)
- /srv/ci (directory)

**Service endpoints to check**:
- Ports listening: 8080 (from configuration)

**Templates rendered**:
- Main application config (rendered once)
- Site-specific configs (rendered twice, one per site)

## Pre-flight checks:
```bash
# Configuration files verification
cat /etc/argument-specs-fixture.conf
grep "enabled=true" /etc/argument-specs-fixture.conf
grep "port=8080" /etc/argument-specs-fixture.conf
grep "ratio=1.5" /etc/argument-specs-fixture.conf
grep "hosts=localhost,example.test" /etc/argument-specs-fixture.conf
grep "timeout=30" /etc/argument-specs-fixture.conf
grep "retries=3" /etc/argument-specs-fixture.conf

# Site-specific configuration - test.example.test
cat /etc/test.example.test.conf
grep "ssl_enabled=true" /etc/test.example.test.conf
ls -ld /srv/test
# Should show directory with 755 permissions, owned by root:root

# Site-specific configuration - ci.example.test
cat /etc/ci.example.test.conf
grep "ssl_enabled=false" /etc/ci.example.test.conf
ls -ld /srv/ci
# Should show directory with 755 permissions, owned by root:root

# File permissions check
stat -c "%a %U:%G %n" /etc/argument-specs-fixture.conf
# Should show 644 root:root /etc/argument-specs-fixture.conf
stat -c "%a %U:%G %n" /etc/test.example.test.conf
# Should show 644 root:root /etc/test.example.test.conf
stat -c "%a %U:%G %n" /etc/ci.example.test.conf
# Should show 644 root:root /etc/ci.example.test.conf

# Port verification
netstat -tulpn | grep 8080
# or
ss -tlnp | grep 8080
```
---
source-path: fixtures/chef-flpath-4648-types
---

# Migration Plan: flpath-4648-types

**TLDR**: This is a simple configuration management cookbook that sets up a basic application with multiple sites. It creates configuration files and directories for an application named 'argument-specs-fixture' with two configured sites: test.example.test and ci.example.test.

## Service Type and Instances

**Service Type**: Configuration Management

**Configured Instances**:

- **test.example.test**:
  - Location/Path: Document root at /srv/test
  - Key Config: SSL enabled (true)
  - Configuration file: /opt/argument-specs-fixture/test.example.test.conf

- **ci.example.test**:
  - Location/Path: Document root at /srv/ci
  - Key Config: SSL disabled (false)
  - Configuration file: /opt/argument-specs-fixture/ci.example.test.conf

## File Structure

```
fixtures/chef-flpath-4648-types/recipes/default.rb
fixtures/chef-flpath-4648-types/attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`fixtures/chef-flpath-4648-types/recipes/default.rb`):
   - Creates base application directory: /opt/argument-specs-fixture
     - Resources: directory (1)
   
   - Creates main application configuration file with environment settings:
     - File: /opt/argument-specs-fixture/application.conf
     - Contains: enabled=true, port=8080, ratio=1.5, timeout=30, retries=3, allowed_hosts=localhost,example.test
     - Resources: file (1)
   
   - Creates document root directory /srv/test for test.example.test
   - Creates site-specific configuration file /opt/argument-specs-fixture/test.example.test.conf
   - Sets document_root and ssl_enabled parameters in the config file for test.example.test
   - Resources: directory (1), file (1)
   
   - Creates document root directory /srv/ci for ci.example.test
   - Creates site-specific configuration file /opt/argument-specs-fixture/ci.example.test.conf
   - Sets document_root and ssl_enabled parameters in the config file for ci.example.test
   - Resources: directory (1), file (1)

## Dependencies

**External cookbook dependencies**: None specified
**System package dependencies**: None specified
**Service dependencies**: None specified

## Credentials

**Detection Summary**: 0 credentials detected across 2 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /opt/argument-specs-fixture/application.conf
- /opt/argument-specs-fixture/test.example.test.conf
- /opt/argument-specs-fixture/ci.example.test.conf
- /srv/test (directory)
- /srv/ci (directory)

**Templates rendered**: None (using file resources with inline content, not templates)

## Pre-flight checks:

```bash
# Directory existence checks
ls -la /opt/argument-specs-fixture
ls -la /srv/test
ls -la /srv/ci

# Configuration file checks
cat /opt/argument-specs-fixture/application.conf
grep -E "enabled|port|ratio|timeout|retries|allowed_hosts" /opt/argument-specs-fixture/application.conf

# Site configuration checks
# Site: test.example.test
cat /opt/argument-specs-fixture/test.example.test.conf
grep "document_root" /opt/argument-specs-fixture/test.example.test.conf
grep "ssl_enabled" /opt/argument-specs-fixture/test.example.test.conf

# Site: ci.example.test
cat /opt/argument-specs-fixture/ci.example.test.conf
grep "document_root" /opt/argument-specs-fixture/ci.example.test.conf
grep "ssl_enabled" /opt/argument-specs-fixture/ci.example.test.conf

# File permissions
stat -c "%a %n" /opt/argument-specs-fixture
stat -c "%a %n" /opt/argument-specs-fixture/application.conf
stat -c "%a %n" /opt/argument-specs-fixture/test.example.test.conf
stat -c "%a %n" /opt/argument-specs-fixture/ci.example.test.conf
stat -c "%a %n" /srv/test
stat -c "%a %n" /srv/ci

# Content validation
grep "enabled=true" /opt/argument-specs-fixture/application.conf
grep "port=8080" /opt/argument-specs-fixture/application.conf
grep "ratio=1.5" /opt/argument-specs-fixture/application.conf
grep "timeout=30" /opt/argument-specs-fixture/application.conf
grep "retries=3" /opt/argument-specs-fixture/application.conf
grep "allowed_hosts=localhost,example.test" /opt/argument-specs-fixture/application.conf
```
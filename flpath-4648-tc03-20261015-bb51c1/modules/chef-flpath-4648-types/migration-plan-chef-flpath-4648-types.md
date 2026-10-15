---
source-path: fixtures/chef-flpath-4648-types
---

# Migration Plan: flpath_4648_types

**TLDR**: This cookbook manages a simple application configuration with two website configurations. It creates a base application directory, configuration files for the application and individual site configurations.

## Service Type and Instances

**Service Type**: Configuration Management (creates directories and configuration files)

**Configured Instances**:

- **test.example.test**: Website configuration with SSL enabled
  - Location/Path: /srv/test (document root)
  - Key Config: ssl_enabled=true

- **ci.example.test**: Website configuration without SSL
  - Location/Path: /srv/ci (document root)
  - Key Config: ssl_enabled=false

## File Structure

```
recipes/default.rb
attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`recipes/default.rb`):
   - Creates base application directory: /opt/argument-specs-fixture
     - Sets mode '0755'
   - Creates main application configuration file: /opt/argument-specs-fixture/application.conf
     - Configures settings: enabled=true, port=8080, ratio=1.5, timeout=30, retries=3
     - Sets allowed_hosts=localhost,example.test
     - Sets mode '0644'
   - Creates document root directory for test.example.test: /srv/test
     - Sets mode '0755'
   - Creates site configuration file for test.example.test: /opt/argument-specs-fixture/test.example.test.conf
     - Contains document_root=/srv/test and ssl_enabled=true
     - Sets mode '0644'
   - Creates document root directory for ci.example.test: /srv/ci
     - Sets mode '0755'
   - Creates site configuration file for ci.example.test: /opt/argument-specs-fixture/ci.example.test.conf
     - Contains document_root=/srv/ci and ssl_enabled=false
     - Sets mode '0644'

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None
**Service dependencies**: None

## Credentials

**Detection Summary**: 0 credentials detected

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /opt/argument-specs-fixture/application.conf
- /opt/argument-specs-fixture/test.example.test.conf
- /opt/argument-specs-fixture/ci.example.test.conf
- /srv/test (directory)
- /srv/ci (directory)

**Service endpoints to check**:
- Ports listening: None (no service is started by this cookbook)
- Unix sockets: None
- Network interfaces: None

**Templates rendered**:
- No .erb templates used, but file resources create 3 configuration files with inline content

## Pre-flight checks:
```bash
# Directory existence
ls -la /opt/argument-specs-fixture/
ls -la /srv/test/
ls -la /srv/ci/

# File content verification - main application config
cat /opt/argument-specs-fixture/application.conf
grep "enabled=true" /opt/argument-specs-fixture/application.conf
grep "port=8080" /opt/argument-specs-fixture/application.conf
grep "ratio=1.5" /opt/argument-specs-fixture/application.conf
grep "timeout=30" /opt/argument-specs-fixture/application.conf
grep "retries=3" /opt/argument-specs-fixture/application.conf
grep "allowed_hosts=localhost,example.test" /opt/argument-specs-fixture/application.conf

# File content verification - site configs
# test.example.test
cat /opt/argument-specs-fixture/test.example.test.conf
grep "document_root=/srv/test" /opt/argument-specs-fixture/test.example.test.conf
grep "ssl_enabled=true" /opt/argument-specs-fixture/test.example.test.conf

# ci.example.test
cat /opt/argument-specs-fixture/ci.example.test.conf
grep "document_root=/srv/ci" /opt/argument-specs-fixture/ci.example.test.conf
grep "ssl_enabled=false" /opt/argument-specs-fixture/ci.example.test.conf

# File permissions
stat -c "%a %n" /opt/argument-specs-fixture/
stat -c "%a %n" /opt/argument-specs-fixture/application.conf
stat -c "%a %n" /opt/argument-specs-fixture/test.example.test.conf
stat -c "%a %n" /opt/argument-specs-fixture/ci.example.test.conf
stat -c "%a %n" /srv/test/
stat -c "%a %n" /srv/ci/
```
---
source-path: fixtures/chef-flpath-4648-types
---

# Migration Plan: flpath-4648-types

**TLDR**: This cookbook configures a simple application by creating a directory structure and a configuration file with various parameter types (boolean, numeric, string, array, hash). It demonstrates different attribute types in Chef.

## Service Type and Instances

**Service Type**: Application Configuration (Static File)

**Configured Instances**:
- **argument-specs-fixture**: Simple configuration deployment
  - Location/Path: /opt/argument-specs-fixture
  - Port: 8080
  - Key Config: Configuration file with various parameter types including boolean, numeric, string, array, and hash values

## File Structure

```
recipes/default.rb
attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`fixtures/chef-flpath-4648-types/recipes/default.rb`):
   - Creates application directory at /opt/argument-specs-fixture
   - Deploys configuration file to /opt/argument-specs-fixture/application.conf with the following parameters:
     - enabled: true (boolean)
     - port: 8080 (integer)
     - ratio: 1.5 (float)
     - timeout: 30 (integer from nested hash)
     - retries: 3 (integer from nested hash)
     - allowed_hosts: localhost,example.test (array joined with commas)
   - Resources: directory (1), file (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None
**Service dependencies**: None

## Credentials

**Detection Summary**: 0 credentials detected across 2 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /opt/argument-specs-fixture (directory)
- /opt/argument-specs-fixture/application.conf (configuration file)

**Service endpoints to check**:
- Ports listening: None (cookbook only creates configuration file)
- Unix sockets: None
- Network interfaces: None

**Templates rendered**:
- No templates are used. Content is generated inline in the recipe using a heredoc.

## Pre-flight checks:
```bash
# Verify directory structure
ls -la /opt/argument-specs-fixture

# Verify configuration file permissions
stat -c "%a %U:%G %n" /opt/argument-specs-fixture/application.conf
# Should show: 644 root:root /opt/argument-specs-fixture/application.conf

# Check configuration file content
cat /opt/argument-specs-fixture/application.conf
# Should contain:
# enabled=true
# port=8080
# ratio=1.5
# timeout=30
# retries=3
# allowed_hosts=localhost,example.test

# Verify individual settings
grep 'enabled=' /opt/argument-specs-fixture/application.conf
grep 'port=' /opt/argument-specs-fixture/application.conf
grep 'ratio=' /opt/argument-specs-fixture/application.conf
grep 'timeout=' /opt/argument-specs-fixture/application.conf
grep 'retries=' /opt/argument-specs-fixture/application.conf
grep 'allowed_hosts=' /opt/argument-specs-fixture/application.conf
```
---
source-path: fixtures/chef-flpath-4648-credentials
---

# Migration Plan: chef-flpath-4648-credentials

**TLDR**: This cookbook creates a configuration file with API credentials including an endpoint URL, username, and checking for the presence of an API token. It's a simple cookbook focused on managing a single credentials configuration file with proper security permissions.

## Service Type and Instances

**Service Type**: Configuration Management (credentials file)

**Configured Instances**:
- **credentials-fixture**: A simple configuration file for API access
  - Location/Path: /etc/x2a-credentials-fixture.conf
  - Key Config: Contains endpoint URL, username, and token status

## File Structure

```
recipes/default.rb
attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`fixtures/chef-flpath-4648-credentials/recipes/default.rb`):
   - Creates a configuration file at `/etc/x2a-credentials-fixture.conf`
   - Populates the file with endpoint URL, username, and token configuration status
   - Sets secure permissions: owner root, group root, mode 0600 (read/write for root only)
   - Resources: file (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None
**Service dependencies**: None

## Credentials

**Detection Summary**: 3 credentials detected across 2 files

**Source**:
  - **Provider**: Internal
  - **URL**: https://example.test/api (endpoint)
  - **Path**: node['argument_specs_credentials']

### API Endpoint

- **Variable(s)**: `node['argument_specs_credentials']['endpoint']`
- **Source file(s)**: attributes/default.rb, recipes/default.rb
- **Current storage**: attribute
- **Usage context**: API endpoint URL used in configuration file

### API Username

- **Variable(s)**: `node['argument_specs_credentials']['username']`
- **Source file(s)**: attributes/default.rb, recipes/default.rb
- **Current storage**: attribute
- **Usage context**: Username for API authentication

### API Token

- **Variable(s)**: `node['argument_specs_credentials']['api_token']`
- **Source file(s)**: recipes/default.rb
- **Current storage**: Not stored in the cookbook (expected to be injected at runtime)
- **Usage context**: API authentication token. The cookbook only checks for its presence and doesn't use the actual value.

## Checks for the Migration

**Files to verify**:
- /etc/x2a-credentials-fixture.conf

**Service endpoints to check**:
- None (this cookbook only creates a configuration file)

**Templates rendered**:
- None (uses file resource with inline content)

## Pre-flight checks:
```bash
# Configuration file existence and permissions
ls -la /etc/x2a-credentials-fixture.conf
# Should show: -rw------- 1 root root [size] [date] /etc/x2a-credentials-fixture.conf

# Configuration content verification
sudo cat /etc/x2a-credentials-fixture.conf
# Should contain:
#   endpoint=https://example.test/api
#   username=fixture-user
#   token_configured=[true/false]

# Verify content matches expected values
grep "endpoint=" /etc/x2a-credentials-fixture.conf
grep "username=" /etc/x2a-credentials-fixture.conf
grep "token_configured=" /etc/x2a-credentials-fixture.conf

# Verify file permissions are correct
stat -c "%a %U %G" /etc/x2a-credentials-fixture.conf
# Should show: 600 root root
```
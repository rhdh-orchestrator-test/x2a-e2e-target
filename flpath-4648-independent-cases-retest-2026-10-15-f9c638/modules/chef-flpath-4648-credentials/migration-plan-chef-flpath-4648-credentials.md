---
source-path: fixtures/chef-flpath-4648-credentials
---

# Migration Plan: chef-flpath-4648-credentials

**TLDR**: This is a simple cookbook that creates a configuration file containing API endpoint information and credentials. It manages a single file at `/etc/x2a-credentials-fixture.conf` with API endpoint, username, and token status information with secure permissions.

## Service Type and Instances

**Service Type**: Configuration Management (creates a single configuration file)

**Configured Instances**:
- **x2a-credentials-fixture**: A configuration file that contains API endpoint and credential information
  - Location/Path: `/etc/x2a-credentials-fixture.conf`
  - Key Config: Contains endpoint URL, username, and token status indicator
  - Permissions: 0600 (read/write by root only)

## File Structure

```
recipes/default.rb
attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`fixtures/chef-flpath-4648-credentials/recipes/default.rb`):
   - Sets up variables from attributes: endpoint, username, api_token
   - Creates configuration file `/etc/x2a-credentials-fixture.conf` with API connection details
   - Sets secure permissions (0600) with root ownership
   - Resources: file (1)

## Dependencies

**External cookbook dependencies**: None specified
**System package dependencies**: None required
**Service dependencies**: None

## Credentials

**Detection Summary**: 3 credential-related values detected across 2 files

**Source**:
  - **Provider**: Internal (Chef attributes)
  - **Path**: node['argument_specs_credentials']

### API Configuration

- **Variable(s)**: `node['argument_specs_credentials']['endpoint']`, `node['argument_specs_credentials']['username']`
- **Source file(s)**: `fixtures/chef-flpath-4648-credentials/attributes/default.rb`, `fixtures/chef-flpath-4648-credentials/recipes/default.rb`
- **Current storage**: attribute
- **Usage context**: API endpoint configuration in configuration file

### API Token

- **Variable(s)**: `node['argument_specs_credentials']['api_token']`
- **Source file(s)**: `fixtures/chef-flpath-4648-credentials/recipes/default.rb`
- **Current storage**: attribute (no default value assigned)
- **Usage context**: Authentication token for API access; intentionally left unassigned as noted in the attributes file comment: "During target-side validation it represents an AAP-injected credential"

## Checks for the Migration

**Files to verify**:
- `/etc/x2a-credentials-fixture.conf`

**Templates rendered**:
- None (using file resource with inline content)

## Pre-flight checks:
```bash
# Configuration file existence and permissions
ls -la /etc/x2a-credentials-fixture.conf
# Should show: -rw------- 1 root root [size] [date] /etc/x2a-credentials-fixture.conf

# Content validation
sudo cat /etc/x2a-credentials-fixture.conf
# Should show:
# endpoint=https://example.test/api
# username=fixture-user
# token_configured=true (or false, depending on if api_token was provided)

# Permissions check
stat -c "%a %U:%G" /etc/x2a-credentials-fixture.conf
# Should show: 600 root:root
```
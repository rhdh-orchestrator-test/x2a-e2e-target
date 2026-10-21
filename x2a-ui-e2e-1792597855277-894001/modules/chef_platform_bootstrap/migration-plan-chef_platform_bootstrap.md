---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef_platform_bootstrap

**TLDR**: No Chef cookbook execution data was available for `chef_platform_bootstrap`. The supplied path, `setup-automate/deploy-automate.sh`, is a file rather than a cookbook directory, and structural analysis reported that it is not a directory. No recipes, resources, packages, templates, attributes, service definitions, iterations, or dependencies were identified. An equivalent Ansible implementation cannot be specified until the actual cookbook directory or recipe files are provided.

## Service Type and Instances

**Service Type**: Undetermined

No recipe files, package resources, or service resources were identified. Therefore, the cookbook cannot be classified as a web server, database, cache, message queue, application server, or other service.

**Configured Instances**: None identified

No collection attributes, `.each` loops, resource iterations, or configured instance names were present in the execution tree.

## File Structure

The execution tree reported zero analyzed files. The supplied path is not a directory, and no cookbook directory structure was available.

```text
chef_platform_bootstrap/
├── recipes/
│   └── default.rb                 # Not found
├── providers/                     # No provider files identified
├── templates/                     # No template files identified
├── attributes/                    # No attribute files identified
└── files/                         # No static files identified

Supplied path:
└── setup-automate/
    └── deploy-automate.sh         # File supplied instead of cookbook directory
```

- Total files analyzed: 0
- No entry recipe found; expected `default.rb`
- No recipe files identified
- No provider files identified
- No template files identified
- No attribute files identified
- No static files identified
- The supplied path is not a directory

## Module Explanation

The cookbook performs no known operations according to the supplied execution tree.

1. **Recipe discovery**
   - No `recipes/default.rb` entry recipe was found.
   - No recipe files were analyzed.
   - No `include_recipe` execution order can be established.

2. **Package installation**
   - No `package` resources were identified.
   - No system package names or versions are available.

3. **Service management**
   - No `service` resources were identified.
   - No systemd units, init scripts, service names, ports, sockets, or restart/reload handlers were identified.

4. **Configuration**
   - No `template`, `file`, `directory`, or `remote_file` resources were identified.
   - No destination paths or configuration variables are available.

5. **Iterations**
   - No loops or collection attributes were identified.
   - There are no item names to expand.

6. **Custom resources**
   - No custom resources were identified.
   - No provider paths were supplied.

Ansible migration cannot safely proceed from the supplied data without inventing cookbook behavior.

## Dependencies

**External cookbook dependencies**: None identified

**System package dependencies**: None identified

**Service dependencies**: None identified

## Credentials

**Detection Summary**: No credentials could be analyzed because zero cookbook files were available for inspection.

**Source**:
  - **Provider**: None detected
  - **URL**: Not available
  - **Path**: Not available

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, vault attributes, environment-variable secrets, hardcoded credentials, database connection strings, or TLS certificate references were present in the supplied structured analysis.

No credentials or secrets were detected in the available cookbook analysis. All available configuration information is non-sensitive or unavailable.

## Checks for the Migration

**Files to verify**: None identified

**Service endpoints to check**: None identified

- Ports listening: None identified
- Unix sockets: None identified
- Network interfaces: None identified

**Templates rendered**: None identified

## Pre-flight checks:

No service-specific pre-flight commands can be authored because no service type, package, service, endpoint, or configuration file was identified.

```bash
# Confirm that the supplied path exists
test -e setup-automate/deploy-automate.sh

# Confirm whether the supplied path is a directory
test -d setup-automate/deploy-automate.sh

# Inspect the supplied path type
file setup-automate/deploy-automate.sh
```

The actual cookbook root must be supplied before migration analysis can continue. It should be the directory containing files such as:

```text
recipes/default.rb
metadata.rb
attributes/default.rb
templates/default/
files/default/
```

Once the cookbook directory is available, the migration should be re-run to determine:

- Service type and installed packages
- Recipe execution order
- All Chef resources
- Iteration collections and exact item names
- Templates and destination paths
- Service ports and sockets
- External cookbook dependencies
- Credentials and secret sources
- Required Ansible roles, tasks, handlers, templates, files, variables, and vault entries
---
source-path: setup-automate/deploy-automate.sh
---

# Migration Plan: chef_automate_infra_server_bootstrap

**TLDR**: No analyzed Chef files or executable recipe were supplied. The target path `setup-automate/deploy-automate.sh` is not a directory, and no cookbook metadata, recipes, resources, instances, packages, services, ports, templates, or credentials were identified. A reliable Chef-to-Ansible migration cannot be created until the actual cookbook directory or a valid execution tree is provided.

## Service Type and Instances

**Service Type**: Undetermined

No service type can be identified because no `metadata.rb`, recipe, package resource, service resource, port, socket, database, cache, web server, or message queue was analyzed.

**Configured Instances**: None identified

No collection attributes or iteration items were provided. There are no confirmed instance names or configuration values to expand into Ansible tasks.

## File Structure

The execution tree contains no files.

**Recipes:**

```text
```

**Providers:**

```text
```

**Templates:**

```text
```

**Attributes:**

```text
```

**Files:**

```text
```

Supplied path:

```text
setup-automate/deploy-automate.sh
```

Structural analysis result:

```text
Error analyzing directory: Path is not a directory: setup-automate/deploy-automate.sh
```

No valid Chef cookbook root was identified.

## Module Explanation

No Chef execution flow is available.

The expected entry point is:

```text
recipes/default.rb
```

Actual result:

```text
No entry recipe found
```

No recipes, `include_recipe` calls, custom resources, providers, templates, package installations, directories, files, users, groups, commands, or services were reported. There is no executable recipe order to reproduce.

No loops or collection attributes were reported, so there are no item names to expand into explicit Ansible tasks.

No service resources or notifications were reported. Service restart and reload handlers cannot be defined without confirmed Chef notification behavior.

## Dependencies

**External cookbook dependencies**: Not available; `metadata.rb` was not analyzed.

**System package dependencies**: None identified.

**Service dependencies**: None identified.

No Ansible package tasks, service tasks, handlers, or role dependencies should be added until the corresponding Chef resources and cookbook dependencies are confirmed.

## Credentials

**Detection Summary**: 0 credentials detected across 0 analyzed files.

No files were available for inspection, so this result does not establish that the unavailable cookbook contains no credentials.

**Source**:
  - **Provider**: Not determinable
  - **URL**: Not available
  - **Path**: Not available

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, vault attribute, environment-variable secret, hardcoded password, API key, database credential, or TLS certificate reference was reported.

Before implementation, inspect the supplied cookbook for:

- Chef data bags and encrypted data bags
- Chef Vault references
- `node['vault']`, `node['secrets']`, or `node['credentials']`
- Passwords, tokens, and API keys in attributes
- `ENV[...]` references in templates
- `.pem`, `.key`, and `.crt` paths
- Database connection strings containing usernames or passwords

Any discovered secrets must use Ansible Vault or the organization’s approved secret-management integration.

## Checks for the Migration

**Files to verify**: No files available from the execution tree

**Service endpoints to check**: None identified

**Templates rendered**: None identified

**Ports listening**: None identified

**Unix sockets**: None identified

**Network interfaces**: None identified

## Pre-flight checks:

```bash
# Confirm the supplied path and its type
test -e setup-automate/deploy-automate.sh
file setup-automate/deploy-automate.sh

# Locate the actual Chef cookbook root once supplied
find . \( -type f -name metadata.rb -o -type f -path '*/recipes/default.rb' \) -print

# Confirm the cookbook contains executable Chef content
find . -type f \( \
  -path '*/recipes/*.rb' -o \
  -path '*/attributes/*.rb' -o \
  -path '*/providers/*.rb' -o \
  -path '*/templates/*.erb' -o \
  -path '*/files/*' \
\) -print
```

No instance-specific service checks can be generated because no instances were identified. After the cookbook is supplied, add validated checks for the discovered service names, ports, sockets, configuration files, templates, and notification behavior.

The migration is blocked until the actual cookbook directory or a regenerated execution tree provides:

- `metadata.rb`
- `recipes/default.rb`
- Included recipe files
- Attribute files
- Provider files
- Templates and static files
- Recipe execution order
- Chef resources and custom resources
- Loop item names and collection values
- Template source and destination paths
- Package names and versions
- Service names and notification behavior
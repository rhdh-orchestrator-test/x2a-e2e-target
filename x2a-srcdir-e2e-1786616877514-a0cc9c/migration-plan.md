# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named 'simple-nginx' with a local dependency on a 'cache' cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible metadata in roles or collections.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for installing and configuring Nginx. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Will be replaced by Ansible metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credential patterns or secrets management detected
- Consider implementing TLS/SSL for Nginx in the Ansible role (not present in current Chef cookbook)

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on external 'nginx' dependency which is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: Migrate Chef attributes to Ansible variables while maintaining the same configuration options.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and configuration, low complexity, no external dependencies
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache cookbook

### Assumptions

1. The Chef cookbooks are used in a standard deployment scenario without custom wrappers or extensions not visible in the repository.
2. The external 'nginx' dependency provides standard Nginx functionality that can be replaced with an Ansible Galaxy role or custom Ansible tasks.
3. No complex templating or configuration is required beyond what's visible in the current codebase.
4. No secrets management or security configurations are needed beyond basic installation and service management.
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata files.
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook "simple-nginx" and a local dependency cookbook "cache". The main cookbook installs and configures Nginx web server, while the cache cookbook installs and configures Redis as a caching solution. The migration scope is relatively small with only two cookbooks to migrate. Given the simplicity of the configurations, this migration should be straightforward with low complexity and could be completed within 1-2 days.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Dependencies need to be mapped to Ansible roles or collections.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Migration consideration: These attributes should be converted to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Migration consideration: This logic should be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Migration consideration: Dependencies need to be mapped to Ansible roles or collections.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Migration consideration: This logic should be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: The cookbooks support Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the metadata.rb files.
- **Virtual Machine Technology**: Not specified in the repository.
- **Cloud Platform**: Not specified in the repository.

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Create a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks.
- No secrets management or credential patterns were detected.

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The Ansible migration will need to either incorporate this functionality directly or use an equivalent Ansible Galaxy role.
- **Configuration management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Low complexity, standalone Redis installation and configuration
2. **simple-nginx cookbook** (Priority 2): Depends on the cache cookbook, but still relatively simple

### Assumptions

1. The external 'nginx' dependency provides standard Nginx installation and configuration capabilities that can be replaced with an Ansible Galaxy role or custom Ansible tasks.
2. No complex Chef-specific features (like search, data bags, or environments) are being used in these cookbooks.
3. The Redis and Nginx configurations are basic and don't include complex customizations.
4. No CI/CD pipeline integration is required for the Ansible migration.
5. The target environments will remain Ubuntu (>= 18.04) and CentOS (>= 7.0).
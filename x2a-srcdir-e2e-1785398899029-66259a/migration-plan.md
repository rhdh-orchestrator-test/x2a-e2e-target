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
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains Nginx configuration attributes that need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for installing and configuring Nginx, which needs to be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis, which needs to be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx tasks
- **cache (local)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credential patterns detected in the examined files
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
  - Network access controls for Redis

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The Ansible migration will need to either incorporate Nginx configuration directly or use an Ansible Galaxy role.
- **Configuration management**: Ensure Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Convert to Ansible role for Redis installation and configuration
2. **simple-nginx cookbook** (Priority 2): Convert to Ansible role for Nginx installation and configuration

### Assumptions

1. The external 'nginx' dependency is used only for installation and basic configuration, as the cookbook itself contains some Nginx configuration code.
2. No complex Chef-specific features (like search, data bags, environments) are being used as they weren't found in the examined files.
3. No custom templates or additional configuration files exist beyond what was discovered.
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+.
5. No special handling is required for Redis data persistence or clustering as the cache cookbook implements only basic Redis installation.
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on deploying and configuring Nginx with Redis caching. The migration scope is relatively small, consisting of two Chef cookbooks with minimal complexity. Based on the repository analysis, this migration is estimated to be a low-complexity effort that could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a simple welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static content creation

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external). Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe file that installs Nginx, ensures the service is running, and creates a simple index page. This logic should be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This should be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible's `ansible.builtin.package` module or the `community.general.nginx_module` for more advanced configurations
- **redis-server (version unspecified)**: Replace with Ansible's `ansible.builtin.package` module for installation and `ansible.builtin.service` module for service management

### Security Considerations

- No explicit security configurations were identified in the repository
- No secrets management or credential patterns were detected
- Basic service security should be maintained during migration:
  - Ensure proper file permissions are set for configuration files
  - Maintain service user configurations (nginx user 'www-data')

### Technical Challenges

- **External dependency handling**: The cookbook depends on an external 'nginx' cookbook which is not included in the repository. The migration will need to incorporate any functionality from this external dependency directly into the Ansible roles.
- **Attribute translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults and overrides.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, no dependencies
2. **simple-nginx cookbook** (Priority 2): Depends on cache cookbook, should be migrated after cache is complete

### Assumptions

1. The external 'nginx' dependency is used only for basic Nginx installation and configuration, which can be handled directly in Ansible without requiring additional modules.
2. No complex Chef-specific features (like search, data bags, environments, etc.) are being used since they weren't evident in the repository.
3. The configuration is intended for a simple web server setup with Redis caching, without complex application deployment or advanced web server configurations.
4. No custom templates or additional configuration files are needed beyond what was found in the repository.
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata files.
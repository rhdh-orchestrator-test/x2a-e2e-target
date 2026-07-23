# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains Chef cookbooks that need to be migrated to Ansible. The primary cookbook is 'simple-nginx' which installs and configures Nginx with a simple welcome page. It has one local dependency ('cache') that installs and configures Redis server. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, ensures the service is running, and creates a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including name, maintainer, description, version, and dependencies. Migration will require mapping these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains default attributes for Nginx configuration including port, user, and worker processes. These will be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates a welcome page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and starts Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in the metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version not specified)**: Replace with Ansible's `nginx` module or the `ansible.posix.package` module to install Nginx
- **redis-server (version not specified)**: Replace with Ansible's `ansible.posix.package` module to install Redis

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644', owner 'root', group 'root')

### Technical Challenges

- **Dependency Management**: The cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or by including the necessary roles directly.
- **Configuration Management**: Nginx configuration attributes will need to be converted to Ansible variables and templates.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, service management, and basic content creation

### Assumptions

1. The external 'nginx' dependency is used only for installation and basic configuration, not for complex custom configurations
2. No custom templates or additional files beyond what's visible in the repository are required
3. No complex conditionals or platform-specific logic exists in the recipes
4. No integration with external services or systems beyond what's explicitly mentioned
5. The cookbooks are intended for basic web server setup and caching functionality
6. No specific security requirements or hardening measures are needed beyond default configurations
7. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
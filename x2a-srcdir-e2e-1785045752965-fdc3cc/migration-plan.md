# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with Redis caching. The migration scope is relatively small, consisting of one main cookbook with one local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: ./
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index.html file.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Create an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No vault/secrets management detected
- Standard service ports (80 for Nginx, default for Redis) should follow security best practices in Ansible roles

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that will need to be replaced with an appropriate Ansible role
- **Configuration Translation**: Converting Chef attributes to Ansible variables while maintaining the same functionality

### Migration Order

1. Create base Ansible project structure with inventory and playbook
2. Migrate cache cookbook to an Ansible role for Redis
3. Migrate simple-nginx cookbook to an Ansible role for Nginx
4. Create integration playbook that combines both roles
5. Test deployment on supported platforms (Ubuntu 18.04+ and CentOS 7.0+)

### Assumptions

1. The external 'nginx' dependency is a standard Chef cookbook without custom modifications
2. No complex Chef-specific features (like search, data bags, etc.) are being used
3. The deployment environment will remain the same (Ubuntu 18.04+ or CentOS 7.0+)
4. No additional configuration beyond what's visible in the repository is required
5. No specific performance tuning or advanced configurations are needed for Nginx or Redis
6. No authentication or SSL/TLS is configured for either service
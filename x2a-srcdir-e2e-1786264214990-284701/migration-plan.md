# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible.
- `attributes/default.rb`: Contains configuration parameters for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index page.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Basic file permissions are set for the index.html file (mode '0644')
- No credentials or secrets management detected
- Vault/secrets management:
  - No Chef encrypted data bags or Chef Vault usage detected
  - No hardcoded credentials found in attributes or templates
  - No SSL/TLS certificate references
  - No environment variable secrets

### Technical Challenges

- **Dependency Management**: The cookbook relies on an external 'nginx' dependency that will need to be replaced with an appropriate Ansible role or task
- **Configuration Translation**: Converting Chef attributes to Ansible variables while maintaining the same functionality
- **Service Management**: Ensuring proper service management in Ansible for both Nginx and Redis services

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, service configuration, and content deployment

### Assumptions

1. The external 'nginx' dependency is used for advanced configurations not visible in the current codebase
2. No custom templates or additional files are used beyond what's visible in the repository
3. No complex conditionals or platform-specific code exists outside the visible files
4. The cookbook is intended for basic web server setup without advanced security or performance tuning
5. No integration with external monitoring or logging systems is required
6. No database integration beyond Redis caching is needed
7. The migration will target the same supported platforms (Ubuntu 18.04+ and CentOS 7.0+)
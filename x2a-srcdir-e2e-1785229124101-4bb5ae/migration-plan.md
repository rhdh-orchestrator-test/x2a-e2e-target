# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: ./
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates an index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the codebase
- No credentials or secrets management was detected
- Standard service security practices should be implemented in the Ansible roles:
  - Firewall rules for Nginx and Redis
  - Proper file permissions for web content

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: Ensure that all Chef attributes are properly mapped to Ansible variables with appropriate defaults.

### Migration Order

1. **cache role** (Priority 1): Convert the Redis cache cookbook to an Ansible role first as it's a dependency for the main cookbook
2. **nginx role** (Priority 2): Convert the main Nginx cookbook to an Ansible role

### Assumptions

- The cookbook is used for basic Nginx and Redis installation without complex configurations
- There are no undocumented runtime dependencies
- The external 'nginx' dependency provides standard Nginx installation and configuration
- No custom templates or additional files are used beyond what's visible in the repository
- No complex Chef-specific features (like search, data bags, or environments) are being used
- The target environment will continue to be Ubuntu 18.04+ or CentOS 7+
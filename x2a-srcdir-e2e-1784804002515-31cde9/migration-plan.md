# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation, service management, and basic content creation. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in the metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible nginx role or direct package installation tasks
- **cache (1.0.0)**: Migrate the local cache cookbook to Ansible tasks for Redis installation and configuration
- **redis-server**: Direct package installation in Ansible

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credentials were detected
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
  - Network access controls

### Technical Challenges

- **External nginx dependency**: The cookbook references an external nginx dependency that isn't included in the repository. The Ansible migration will need to implement the functionality directly or use a community role.
- **Attribute mapping**: Ensure Chef attributes are properly mapped to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, depends on cache

### Assumptions

1. The external nginx dependency is used only for its core functionality (installation and service management), which is already partially implemented in the simple-nginx cookbook's default recipe.
2. No complex templating or configuration is required beyond what's visible in the repository.
3. The cache cookbook is only used for Redis installation and not for more complex caching strategies.
4. No specific security hardening is required beyond standard practices.
5. No custom configurations beyond the attributes defined in attributes/default.rb are needed.
6. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+.
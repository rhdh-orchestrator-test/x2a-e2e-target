# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook with one local dependency cookbook. Based on the complexity and size, this migration can likely be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates an index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the 'supports' metadata entries)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible community.nginx collection or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current cookbooks
- No secrets management or credentials were detected in the reviewed files
- Standard service security practices should be applied in the Ansible roles:
  - Firewall configuration for Nginx and Redis
  - Proper file permissions for web content
  - Redis access control configuration

### Technical Challenges

- **External dependency**: The 'nginx' cookbook is referenced but not included in the repository. The Ansible migration will need to implement the functionality directly rather than relying on an external dependency.
- **Configuration management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly mapped to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Convert the Redis cache cookbook first as it's a dependency for the main cookbook
2. **nginx role** (Priority 2): Convert the main Nginx cookbook after the cache role is complete

### Assumptions

1. The external 'nginx' cookbook is used primarily for installation and basic configuration, which can be implemented directly in Ansible.
2. No complex templating or configuration is present beyond what's visible in the repository.
3. No custom resources or libraries are being used that would require special handling.
4. The cookbook is designed for Ubuntu 18.04+ or CentOS 7+ environments as specified in the metadata.
5. No integration with external services or authentication systems is required.
6. No complex data structures or environment-specific configurations exist beyond the basic attributes defined.
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook infrastructure focused on deploying and configuring Nginx with Redis caching. The codebase is relatively small and straightforward, consisting of a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks. The 'nginx' dependency is external and not included in the repository.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port (80), user (www-data), and worker processes.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index.html file.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role from Ansible Galaxy or create a custom role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443
  - TLS/SSL implementation (not present in current code)
  - Proper file permissions for web content

### Technical Challenges

- **External dependency handling**: The current cookbook depends on an external 'nginx' cookbook that is not included in the repository. The Ansible migration will need to implement all necessary Nginx configurations directly.
- **Attribute translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, configuration, and content deployment

### Assumptions

1. The external 'nginx' cookbook is used for advanced configurations not visible in the current codebase
2. No complex templating or conditional logic is present in the current implementation
3. No secrets management or security-sensitive configurations are present
4. The target environment matches the supported platforms (Ubuntu 18.04+ or CentOS 7.0+)
5. No CI/CD pipeline integration is required for the migration
6. No custom resources or libraries are used in the current implementation
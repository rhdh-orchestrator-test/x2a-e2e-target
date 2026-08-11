# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named 'simple-nginx' with a local dependency on a 'cache' cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Dependencies need to be mapped to Ansible roles or collections.
- `attributes/default.rb`: Defines default attributes for Nginx configuration. Migration consideration: These attributes should be converted to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing Nginx, ensuring the service is running, and creating a simple index page. Migration consideration: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines metadata for the cache cookbook. Migration consideration: Convert to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Migration consideration: Convert to Ansible tasks for Redis installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (explicitly specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx collection or create a custom Nginx role
- **cache (1.0.0)**: Convert to an Ansible role for Redis installation and configuration
- **redis-server**: Ensure appropriate package installation in the Ansible playbook

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443 (Nginx) and 6379 (Redis)
  - Redis password protection (not present in current code but recommended)
  - Nginx server hardening (TLS configuration, security headers)

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration management**: Ensure that Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, service management, and content creation

### Assumptions

1. The 'nginx' external dependency is used only for basic installation and configuration, which can be replaced with standard Ansible tasks or community roles.
2. No complex templating or configuration is present beyond what's visible in the repository.
3. No secrets management or sensitive data handling is required based on the current codebase.
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata files.
5. The simple index.html content can be directly translated without any dynamic content considerations.
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook (simple-nginx) and one local dependency cookbook (cache). The migration complexity is low to moderate, with an estimated timeline of 1-2 days for a complete migration to Ansible.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Convert dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains Nginx configuration attributes. Migration consideration: Convert to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Migration consideration: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for cache cookbook. Migration consideration: Convert to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Redis installation and service configuration. Migration consideration: Convert to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` module or community.general collection
- **redis-server (unspecified version)**: Replace with Ansible's `apt`/`yum` modules for installation and `systemd` module for service management

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Consider implementing TLS/SSL for Nginx in the Ansible roles

### Technical Challenges

- **External dependency handling**: The cookbook depends on an external 'nginx' cookbook that isn't included in the repository. The Ansible migration will need to implement the functionality directly rather than relying on external dependencies.
- **Platform compatibility**: Ensure the Ansible roles work on both Ubuntu and CentOS as specified in the original metadata.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, service management, and basic content

### Ansible Role Structure

Proposed Ansible structure:

```
roles/
  nginx/
    defaults/
      main.yml  # Convert from attributes/default.rb
    tasks/
      main.yml  # Convert from recipes/default.rb
    meta/
      main.yml  # Convert from metadata.rb
  redis_cache/
    tasks/
      main.yml  # Convert from cookbooks/cache/recipes/default.rb
    meta/
      main.yml  # Convert from cookbooks/cache/metadata.rb
playbooks/
  site.yml      # Main playbook to include both roles
```

### Assumptions

1. The cookbook is intended for basic Nginx and Redis installation without complex configurations
2. No custom templates or configuration files are used beyond what's explicitly shown
3. No specific Nginx configuration beyond the default is required
4. No specific Redis configuration beyond the default is required
5. No security hardening is implemented in the current cookbooks
6. No backup or monitoring solutions are implemented
7. The external 'nginx' dependency might contain additional configurations not visible in this repository
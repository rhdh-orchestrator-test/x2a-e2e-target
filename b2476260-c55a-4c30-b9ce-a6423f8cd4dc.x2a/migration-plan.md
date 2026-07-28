# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook called `simple-nginx` and a local dependency cookbook called `cache`. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and platform support. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be translated to Ansible role defaults.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be translated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will need to be translated to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be translated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **cache (local)**: Migrate to a new Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were found in the cookbooks
- No secrets management or credentials were detected
- Standard service security considerations for Nginx and Redis should be implemented in the Ansible roles

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collection dependencies.
- **Configuration Management**: Ensure that Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and configuration, no dependencies
2. **nginx role** (Priority 2): Depends on cache role, but still relatively simple

### Assumptions

1. The cookbook is used in a simple environment without complex integrations
2. There are no custom templates or additional files beyond what was discovered
3. The external nginx dependency uses standard configurations that can be replaced with common Ansible patterns
4. No complex Chef-specific features (like search, data bags, or environments) are being used
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+

## Migration Steps

1. **Create Ansible Role Structure**:
   - Create `roles/nginx` and `roles/redis` directories
   - Set up standard Ansible role structure (defaults, tasks, handlers, meta)

2. **Migrate Cache Cookbook**:
   - Create tasks to install and enable Redis server
   - Add appropriate handlers for service restart

3. **Migrate Simple-Nginx Cookbook**:
   - Create tasks to install and enable Nginx
   - Create task to deploy the welcome page
   - Add appropriate handlers for service restart
   - Migrate attributes to defaults/main.yml

4. **Create Playbook**:
   - Create a main playbook that includes both roles
   - Ensure proper role execution order

5. **Testing**:
   - Test the migrated roles individually
   - Test the complete playbook
   - Verify functionality matches original Chef implementation

## Conclusion

This migration is relatively straightforward due to the simplicity of the cookbooks. The main focus should be on ensuring that the Nginx configuration is properly translated from Chef attributes to Ansible variables, and that the Redis installation works correctly. The estimated effort is low, and the migration can be completed in 1-2 days by a single developer familiar with both Chef and Ansible.
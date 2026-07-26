# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` with a local dependency on a `cache` cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata, dependencies, and supported platforms. Will be replaced by Ansible role metadata in `meta/main.yml`.
- `attributes/default.rb`: Contains default attributes for nginx configuration. Will be migrated to Ansible role defaults in `defaults/main.yml`.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credentials or secrets management detected
- Standard service ports (nginx:80, redis) should follow security best practices in Ansible

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collection dependencies.
- **Configuration Management**: Migrate Chef attributes to Ansible variables, ensuring proper variable precedence.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation with configuration from variables

### Assumptions

1. The cookbook is used for basic Nginx and Redis installation without complex configurations
2. No custom templates or additional files beyond what's visible in the repository
3. No external Berksfile or Policyfile exists for managing the external nginx dependency
4. No specific security requirements beyond standard service configurations
5. The cookbook is intended for testing purposes as indicated in the README

## Migration Steps

1. **Create Ansible Role Structure**:
   - Create `roles/nginx` and `roles/redis_cache` directories
   - Set up standard Ansible role structure for each

2. **Migrate Cache Cookbook**:
   - Create `roles/redis_cache/tasks/main.yml` for Redis installation and service management
   - Create `roles/redis_cache/meta/main.yml` for role metadata

3. **Migrate Nginx Cookbook**:
   - Create `roles/nginx/tasks/main.yml` for Nginx installation and service management
   - Create `roles/nginx/defaults/main.yml` for variables (from Chef attributes)
   - Create `roles/nginx/templates` for any configuration templates
   - Create `roles/nginx/files` for static files (like index.html)

4. **Create Playbook**:
   - Create a main playbook that includes both roles
   - Ensure proper variable definitions and role dependencies

5. **Testing**:
   - Test the playbook against Ubuntu 18.04+ and CentOS 7.0+ environments
   - Verify Nginx and Redis services are running correctly

6. **Documentation**:
   - Update documentation to reflect Ansible usage
   - Document variables and their defaults
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` that installs and configures Nginx with basic settings. The cookbook follows a metadata-only dependency strategy and includes one local dependency (`cache` cookbook) and one external dependency (`nginx` cookbook). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs and configures Nginx web server with basic settings
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible metadata in `meta/main.yml`.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for installing and configuring Nginx. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook. Will be replaced by Ansible metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **cache (1.0.0)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **External Dependencies**: The cookbook depends on an external `nginx` cookbook which is declared but not included. The migration will need to either use an Ansible Galaxy role or implement the required functionality directly.
- **Configuration Management**: Ensure that Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The current Chef implementation is minimal and doesn't include complex configurations or templates for Nginx
2. The external `nginx` dependency is used for additional configuration not visible in the current codebase
3. No custom Nginx configuration files are being managed beyond the basic installation
4. No SSL/TLS configuration is present in the current implementation
5. No virtual hosts or complex server blocks are configured
6. The Redis configuration in the cache cookbook uses default settings without customization

## Ansible Migration Details

### Role Structure

The migration will create two Ansible roles:

1. **nginx_web**
   - Based on the simple-nginx cookbook
   - Will include tasks for installing Nginx, managing the service, and creating basic content

2. **redis_cache**
   - Based on the cache cookbook
   - Will include tasks for installing Redis and managing the service

### Variable Mapping

Chef attributes will be mapped to Ansible variables:

```yaml
# group_vars/all.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Task Mapping

Chef resources will be mapped to Ansible modules:

- `package` resource → `ansible.builtin.package` module
- `service` resource → `ansible.builtin.service` module
- `file` resource → `ansible.builtin.copy` or `ansible.builtin.template` module

### Playbook Structure

```yaml
# site.yml
---
- name: Configure web servers
  hosts: webservers
  become: true
  roles:
    - redis_cache
    - nginx_web
```

This migration plan provides a comprehensive roadmap for converting the Chef cookbooks to Ansible roles while maintaining the same functionality and dependencies.
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook "simple-nginx" and a local dependency cookbook "cache". The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Convert dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains default attributes for nginx configuration. Migration consideration: Convert to Ansible variables.
- `recipes/default.rb`: Main recipe for nginx installation and configuration. Migration consideration: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Migration consideration: Convert to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management. Migration consideration: Convert to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` module or community.general collection
- **redis-server (unspecified version)**: Replace with Ansible's `apt`/`yum` modules for installation and `service` module for management

### Security Considerations

- No explicit security configurations identified in the current codebase
- Vault/secrets management: No credentials detected in the reviewed files

### Technical Challenges

- **Dependency Management**: The cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: Ensure that the Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The cookbook is designed for testing purposes and may not represent a production-ready configuration
2. The external 'nginx' dependency is expected to be resolved through Berkshelf or Policyfile, but these files are not present in the repository
3. No custom templates or complex configurations are used beyond what's visible in the recipes
4. No security hardening or custom configurations are applied to either Nginx or Redis
5. The cookbook is intended for Ubuntu 18.04+ or CentOS 7.0+ environments as specified in the metadata files

## Ansible Migration Details

### Role Structure

The migration will create two Ansible roles:

1. **nginx_role**:
   - `defaults/main.yml`: Variables converted from attributes/default.rb
   - `tasks/main.yml`: Tasks converted from recipes/default.rb
   - `meta/main.yml`: Dependencies information from metadata.rb

2. **cache_role**:
   - `tasks/main.yml`: Redis installation and service tasks
   - `meta/main.yml`: Basic role metadata

### Variable Mapping

Chef attributes will be converted to Ansible variables:
- `default['nginx']['port']` → `nginx_port`
- `default['nginx']['user']` → `nginx_user`
- `default['nginx']['worker_processes']` → `nginx_worker_processes`

### Task Conversion Examples

**From Chef:**
```ruby
package 'nginx' do
  action :install
end

service 'nginx' do
  action [:enable, :start]
end
```

**To Ansible:**
```yaml
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Ensure nginx service is running
  service:
    name: nginx
    state: started
    enabled: yes
```

### Playbook Structure

A main playbook will be created to orchestrate the roles:

```yaml
---
- name: Deploy Nginx with Redis Cache
  hosts: web_servers
  become: yes
  roles:
    - cache_role
    - nginx_role
```

## Timeline Estimate

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours
- Total: 12 hours (1-2 days)
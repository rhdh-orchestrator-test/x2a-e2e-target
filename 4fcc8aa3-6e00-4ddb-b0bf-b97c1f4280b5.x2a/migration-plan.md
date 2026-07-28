# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on Nginx installation with a Redis cache dependency. The migration scope is relatively small, consisting of two Chef cookbooks with minimal complexity. The estimated timeline for migration is 1-2 days for a skilled Ansible developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration as a caching layer
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external). Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains Nginx configuration attributes that should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration, to be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Redis server installation and configuration, to be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or the `community.general.nginx_*` modules
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management were identified in the repository
- Standard web server security practices should be implemented in the Ansible roles:
  - Nginx configuration hardening
  - Redis security configuration (password, bind address)

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency which is not included in the repository. The Ansible migration will need to either:
  1. Implement the nginx functionality directly
  2. Use the community.nginx collection from Ansible Galaxy

- **Configuration Management**: Ensure that the Nginx configuration attributes from `attributes/default.rb` are properly mapped to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, depends on cache

### Assumptions

1. The external 'nginx' dependency is used only for basic Nginx installation and configuration
2. No complex Chef resources or custom resources are being used beyond what's visible in the repository
3. No secrets management or vault integration is required
4. No complex templating or file management beyond the basic index.html file
5. No custom extensions or plugins for Nginx are required
6. The Redis cache is a standalone installation without complex configuration

## Ansible Migration Structure

The proposed Ansible structure will consist of:

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── defaults/main.yml  # From attributes/default.rb
│   │   ├── tasks/main.yml     # From recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # From file resource in recipe
│   └── redis_cache/
│       ├── tasks/main.yml     # From cookbooks/cache/recipes/default.rb
│       └── defaults/main.yml  # Default Redis configuration
└── site.yml                   # Main playbook
```

## Timeline Estimate

- **Analysis and Planning**: 2 hours (completed)
- **Role Development**:
  - redis_cache role: 2 hours
  - nginx role: 4 hours
- **Testing**: 4 hours
- **Documentation**: 2 hours
- **Total**: 14 hours (approximately 2 days)
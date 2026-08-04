# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on Nginx installation with a Redis cache dependency. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. Given the limited complexity, this migration can likely be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external). Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains Nginx configuration attributes that should be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration, to be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or the `community.general.nginx_*` modules
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the repository
- No secrets management or credential patterns were detected
- Consider implementing TLS/SSL for Nginx in the Ansible role as a security enhancement

### Technical Challenges

- **Attribute to Variable Mapping**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables with appropriate defaults
- **Service Management**: Ensure proper service management for both Nginx and Redis in the Ansible roles
- **External Dependencies**: The external 'nginx' dependency needs to be replaced with appropriate Ansible Galaxy roles or collections

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration that depends on the cache role

### Assumptions

1. The external 'nginx' dependency in Chef was used only for advanced configurations not shown in the simple recipe
2. No complex templating or configuration management is required beyond what's visible in the repository
3. No custom resources or libraries are used in either cookbook
4. No specific operating system optimizations are required beyond basic package installation
5. No specific security hardening is implemented in the current cookbooks
6. No integration with external services or APIs is required
7. The Redis cache is running on the same host as the Nginx server

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventories/
│   └── development/
│       ├── group_vars/
│       │   └── all.yml  # Variables from attributes/default.rb
│       └── hosts
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Default variables from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Tasks from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Template for the welcome page
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Tasks from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Any default variables for Redis
└── site.yml  # Main playbook that includes both roles
```

## Timeline Estimate

- **Analysis and Planning**: 2 hours (completed)
- **Role Development**: 4 hours
  - Redis cache role: 1 hour
  - Nginx role: 3 hours
- **Testing**: 2 hours
- **Documentation**: 1 hour
- **Total**: 9 hours (approximately 1-2 days of work)
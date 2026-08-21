# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on Nginx installation with a Redis cache dependency. The migration scope is relatively small, consisting of two Chef cookbooks with minimal complexity. The estimated timeline for migration is 1-2 days for an experienced Ansible developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration as a caching layer
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Will be replaced by Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains Nginx configuration attributes that will be migrated to Ansible role defaults.
- `recipes/default.rb`: Contains the main Nginx installation and configuration logic to be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata with no external dependencies.
- `cookbooks/cache/recipes/default.rb`: Contains Redis installation and service management to be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or direct package installation using the `apt`/`yum` modules
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **External nginx dependency**: The cookbook depends on an external 'nginx' cookbook that isn't included in the repository. The migration will need to either:
  1. Implement equivalent functionality directly in Ansible tasks
  2. Use community.general.nginx_* modules for configuration
  3. Use an existing Ansible Galaxy nginx role

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation with basic configuration

### Ansible Structure Plan

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Migrated from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Migrated from metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Migrated from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from static content
│   └── redis_cache/
│       ├── meta/
│       │   └── main.yml  # Migrated from cookbooks/cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Migrated from cookbooks/cache/recipes/default.rb
└── site.yml  # Main playbook
```

### Assumptions

1. The external 'nginx' cookbook is used only for its package installation and service management capabilities, which can be directly implemented in Ansible.
2. No complex configuration templates or additional files are needed beyond what's visible in the repository.
3. The Redis cache and Nginx are intended to run on the same host.
4. No specific performance tuning or advanced configurations are required for either Nginx or Redis.
5. No authentication or TLS/SSL configurations are needed for the initial migration.
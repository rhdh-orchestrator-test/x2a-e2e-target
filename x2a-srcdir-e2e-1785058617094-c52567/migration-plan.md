# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook with a local dependency cookbook. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs and configures Nginx with a basic welcome page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible nginx role or direct package installation tasks
- **cache (1.0.0)**: Replace with Ansible Redis role or direct package installation tasks
- **redis-server**: Direct package installation in Ansible tasks

### Security Considerations

- No explicit security configurations identified in the current codebase
- Vault/secrets management:
  - No credentials detected in the repository
  - No SSL/TLS certificate references found
  - No encrypted data bags or Chef Vault usage identified

### Technical Challenges

- **Attribute Translation**: Convert Chef attributes to Ansible variables, particularly the Nginx configuration attributes
- **Service Management**: Ensure proper service management for both Nginx and Redis services
- **Dependency Management**: Handle the external nginx dependency that was previously managed through Chef

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, depends on cache

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Convert Chef attributes here
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Install nginx, create index.html
│   │   ├── templates/
│   │   │   └── index.html.j2  # Template for welcome page
│   │   └── defaults/
│   │       └── main.yml  # Nginx configuration variables
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Install and configure Redis
│       └── defaults/
│           └── main.yml  # Redis configuration variables
└── site.yml  # Main playbook
```

### Variable Mapping

Chef attributes to Ansible variables:
- `default['nginx']['port']` → `nginx_port`
- `default['nginx']['user']` → `nginx_user`
- `default['nginx']['worker_processes']` → `nginx_worker_processes`

### Assumptions

1. The cookbook is used in a simple environment without complex Chef-specific features
2. The external nginx dependency doesn't contain critical customizations
3. No custom templates or additional files are used beyond what's visible in the repository
4. No complex conditionals or platform-specific code is present
5. No integration with external services or authentication systems
6. The Redis configuration uses default settings without customization
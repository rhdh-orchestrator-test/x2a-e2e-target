# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with two cookbooks that perform basic installation and configuration of Nginx and Redis. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
  - Migration consideration: Convert dependencies to Ansible Galaxy requirements
  
- `attributes/default.rb`: Contains configuration variables for Nginx
  - Migration consideration: Convert to Ansible variables in vars/ or defaults/

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credentials or secrets management detected
- Standard service ports (80 for Nginx, 6379 for Redis) should follow security best practices in Ansible

### Technical Challenges

- **External dependency handling**: The cookbook references an external 'nginx' dependency that would need to be replaced with an appropriate Ansible Galaxy role or custom role
- **Configuration management**: Ensure Nginx configuration parameters from attributes are properly mapped to Ansible variables

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventory/
│   └── hosts.ini
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/   # Converted from simple-nginx cookbook
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── templates/
│   │   │   └── index.html.j2
│   │   └── defaults/
│   │       └── main.yml
│   └── redis/   # Converted from cache cookbook
│       ├── tasks/
│       │   └── main.yml
│       └── defaults/
│           └── main.yml
├── requirements.yml  # For external dependencies
└── site.yml         # Main playbook
```

### Assumptions

1. The cookbook is intended for basic Nginx and Redis installation without complex configurations
2. No custom templates or configuration files are used beyond what's visible in the repository
3. No specific security hardening is required beyond default installations
4. The external 'nginx' dependency doesn't contain critical functionality that would need special handling
5. No specific user management or authentication is required
6. No specific backup or maintenance tasks are included
7. No specific monitoring or logging configurations are required
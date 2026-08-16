# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook structure for Nginx deployment with a Redis cache dependency. The migration scope includes the main simple-nginx cookbook at the root directory and the cache cookbook in the cookbooks directory. Based on the complexity and size, this migration can be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

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

- `metadata.rb`: Defines cookbook metadata, dependencies, and supported platforms
  - Migration consideration: Convert dependencies to Ansible Galaxy requirements
  
- `attributes/default.rb`: Contains configuration parameters for Nginx
  - Migration consideration: Convert to Ansible variables in defaults/main.yml

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible Redis role or use `geerlingguy.redis`

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be implemented:
  - Firewall rules for Nginx and Redis
  - Redis password protection (not implemented in current code)
  - Nginx SSL configuration (not implemented in current code)
- Vault/secrets management:
  - No credentials detected in the current codebase

### Technical Challenges

- **Simple Migration**: The codebase is straightforward with minimal complexity
- **External Dependencies**: The external nginx dependency needs to be replaced with an appropriate Ansible role
- **Configuration Management**: Ensure Nginx configuration parameters are properly translated to Ansible variables

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation dependent on cache

### Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── handlers/
│           └── main.yml  # Service restart handlers
├── playbook.yml
└── requirements.yml  # For external dependencies
```

### Assumptions

1. The cookbook is intended for a simple Nginx deployment with Redis caching
2. No complex configuration or customization is required
3. No security hardening is implemented in the current code
4. The cookbook is designed for Ubuntu 18.04+ or CentOS 7+ environments
5. No specific cloud platform requirements are present
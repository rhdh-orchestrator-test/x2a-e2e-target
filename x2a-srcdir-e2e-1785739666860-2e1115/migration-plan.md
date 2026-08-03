# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named 'simple-nginx' that requires migration to Ansible. The cookbook is relatively simple with one local dependency ('cache') and one external dependency ('nginx'). The migration scope is small, with only two cookbooks to convert. Based on the complexity and size, this migration should be straightforward and could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic nginx installation, service management, static index page creation

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata, dependencies, and supported platforms
  - Migration consideration: Convert dependencies to Ansible Galaxy requirements
  
- `attributes/default.rb`: Defines default attributes for nginx configuration
  - Migration consideration: Convert to Ansible variables in defaults/main.yml

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **cache (1.0.0)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Firewall rules for nginx and Redis
  - Redis password protection (not implemented in the original cookbook)

### Technical Challenges

- **External Dependencies**: The nginx dependency is declared but not included in the repository. The Ansible migration will need to either:
  1. Use a community nginx role from Ansible Galaxy
  2. Create a custom nginx role based on the Chef cookbook's functionality

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Depends on cache, should be migrated after

### Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventories/
│   └── development/
│       ├── group_vars/
│       │   └── all.yml  # Variables from attributes/default.rb
│       └── hosts
├── roles/
│   ├── cache/           # Converted from cookbooks/cache
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   └── tasks/
│   │       └── main.yml # Logic from cookbooks/cache/recipes/default.rb
│   └── nginx/           # Converted from root cookbook
│       ├── defaults/
│       │   └── main.yml # Variables from attributes/default.rb
│       └── tasks/
│           └── main.yml # Logic from recipes/default.rb
├── site.yml             # Main playbook
└── requirements.yml     # External dependencies (if using Galaxy roles)
```

### Assumptions

1. The nginx cookbook referenced in the metadata.rb is a standard community cookbook
2. No custom templates or configurations are needed beyond the basic installation
3. No secrets management is required for this simple setup
4. The cookbook is intended for testing purposes only, as indicated in the README
5. Redis is used without authentication or custom configuration
6. The nginx setup is minimal without complex virtual hosts or SSL configuration
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains Chef cookbooks for Nginx deployment with a local cache dependency. The migration scope includes two Chef cookbooks: a main cookbook in the root directory and a cache cookbook in the cookbooks directory. Based on the repository analysis, this is a straightforward migration that could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains Nginx configuration attributes that should be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and configuration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx collection or create a custom Nginx role
- **cache (1.0.0)**: Migrate the local cache cookbook to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management were identified in the repository
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for Nginx configuration files
  - Redis security configuration (password, bind address, etc.)

### Technical Challenges

- **Simple Migration**: The cookbooks are straightforward with minimal complexity
- **Attribute Translation**: Chef attributes need to be mapped to Ansible variables
- **External Dependency**: The external 'nginx' dependency is declared but not included in the repository. The actual implementation details will need to be determined during migration.

### Migration Order

1. **cache role** (Priority 1): Create an Ansible role for Redis cache installation and configuration
2. **nginx role** (Priority 2): Create an Ansible role for Nginx installation and configuration

### Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── site.yml  # Main playbook
```

### Assumptions

1. The external 'nginx' dependency likely provides additional Nginx configuration options not visible in this repository
2. No complex configuration management or templating is required based on the simple nature of the recipes
3. No secrets management or security hardening is implemented in the current cookbooks
4. The cookbooks are designed for testing purposes as indicated in the README.md and may not represent production-ready code
5. The Redis cache implementation is basic and doesn't include advanced configuration
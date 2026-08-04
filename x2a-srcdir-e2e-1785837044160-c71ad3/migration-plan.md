# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with basic settings. The migration scope is relatively small, consisting of one main cookbook and one local dependency cookbook. Based on the repository analysis, this is a straightforward migration that could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains configuration variables for Nginx. Will be migrated to Ansible role defaults/main.yml.
- `recipes/default.rb`: Contains the main installation and configuration logic. Will be migrated to Ansible tasks/main.yml.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a new Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No credential patterns or secrets management were detected
- Basic service security should be implemented in the Ansible roles:
  - Firewall rules for Nginx (ports 80/443)
  - Redis security (bind address, authentication)

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that will need to be replaced with an appropriate Ansible role or task
- **Configuration Management**: Ensure that all Nginx configuration parameters from attributes are properly mapped to Ansible variables

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content deployment

### Ansible Structure

The proposed Ansible structure will be:

```
ansible-simple-nginx/
├── inventories/
│   └── development/
│       ├── group_vars/
│       │   └── all.yml
│       └── hosts
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Converted from metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis_cache/
│       ├── defaults/
│       │   └── main.yml
│       ├── meta/
│       │   └── main.yml  # Converted from cookbooks/cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
└── site.yml  # Main playbook
```

### Assumptions

1. The cookbook is intended for basic Nginx installation without complex configurations
2. Redis is used as a simple cache without custom configurations
3. No specific security requirements beyond basic service setup
4. No custom templates or additional files beyond what's visible in the repository
5. The external 'nginx' dependency doesn't contain critical custom configurations that would need special handling
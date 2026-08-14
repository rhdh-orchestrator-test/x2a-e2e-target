# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook "simple-nginx" and a local dependency cookbook "cache". The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and platform support. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be translated to Ansible role defaults.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be translated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will need to be translated to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be translated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the `supports` statements in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user management
  - Firewall rules for Nginx and Redis services

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or by including roles directly.
- **Attribute Translation**: Chef attributes need to be translated to Ansible variables, maintaining the same structure and defaults.

### Migration Order

1. **cache role**: Start with the Redis cache role as it's a dependency for the main cookbook
2. **nginx role**: Create the Nginx role with the basic configuration and welcome page

### Assumptions

- The cookbook is designed for testing purposes and may not include all production-ready configurations
- The nginx dependency is expected to be an external cookbook not included in the repository
- No complex configurations or templates are used in either cookbook
- No secrets management or security-specific configurations are present
- The cookbooks are designed to work on Ubuntu 18.04+ and CentOS 7+ systems
- Chef version 16.0 or higher is required for the original cookbooks

## Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventories/
│   └── development/
│       ├── group_vars/
│       │   └── all.yml  # Variables from attributes/default.rb
│       └── hosts
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # From attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # From metadata.rb
│   │   └── tasks/
│   │       └── main.yml  # From recipes/default.rb
│   └── redis_cache/
│       ├── meta/
│       │   └── main.yml  # From cookbooks/cache/metadata.rb
│       └── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
├── requirements.yml  # For external dependencies
└── site.yml  # Main playbook
```

## Migration Timeline

Given the simplicity of the cookbooks:

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1-2 days)
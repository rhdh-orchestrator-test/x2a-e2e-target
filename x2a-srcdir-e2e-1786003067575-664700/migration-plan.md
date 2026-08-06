# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook with a local dependency cookbook. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs and configures Nginx with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static content creation

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible metadata or requirements.yml.
- `attributes/default.rb`: Contains configuration variables for Nginx including port, user, and worker processes. Will be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the codebase
- No credentials or secrets management was detected
- Standard service security practices should be applied in the Ansible roles:
  - Nginx: Configure proper file permissions, disable unused modules
  - Redis: Configure authentication if needed, bind to appropriate interfaces

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that will need to be replaced with an appropriate Ansible role or custom tasks
- **Configuration Translation**: Attributes in Chef will need to be converted to Ansible variables with appropriate defaults

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Ansible Structure Recommendation

```
ansible-nginx/
├── inventories/
│   └── development/
│       ├── hosts
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis_cache/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
├── playbook.yml
└── requirements.yml  # For external dependencies
```

### Assumptions

1. The cookbook is intended for basic Nginx installation without complex configurations
2. Redis is used as a simple cache without custom configurations
3. No specific security requirements are present in the current implementation
4. No custom templates or additional files are needed beyond what's explicitly defined in the recipes
5. The external nginx dependency provides standard Nginx functionality that can be replaced with a common Ansible Galaxy role
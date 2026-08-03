# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook called "simple-nginx" that installs and configures Nginx with basic settings. The repository is relatively small and straightforward, consisting of a main cookbook with one local dependency cookbook called "cache" that installs Redis. The migration complexity is low, with an estimated timeline of 1-2 days for complete conversion to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs and configures Nginx web server with basic settings
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple Redis cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including name, version, dependencies, and supported platforms. Will need to be converted to Ansible metadata in galaxy.yml.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be converted to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will need to be converted to Ansible metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible community.general.nginx or builtin package module
- **cache (local)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Ensure proper file permissions for Nginx configuration files
  - Configure Redis with authentication if exposed beyond localhost

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook which is not present in the repository. The Ansible migration will need to implement the functionality directly rather than relying on external dependencies.
- **Configuration Management**: Ensure that all Nginx configuration parameters from attributes/default.rb are properly mapped to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Convert to Ansible role first as it's a dependency for the main cookbook
2. **simple-nginx cookbook** (Priority 2): Convert to Ansible role after the cache role is complete

### Ansible Structure Recommendation

```
ansible-simple-nginx/
├── galaxy.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── meta/
│   │       └── main.yml  # Converted from metadata.rb
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── meta/
│           └── main.yml  # Converted from cookbooks/cache/metadata.rb
└── playbooks/
    └── site.yml  # Main playbook that includes both roles
```

### Assumptions

1. The nginx cookbook dependency is used only for basic installation and configuration, which can be directly implemented in Ansible.
2. No complex Chef-specific features (like search, data bags, etc.) are being used in the current implementation.
3. The Redis configuration in the cache cookbook is minimal and doesn't require complex configuration.
4. No custom templates or files are being used beyond what's visible in the repository.
5. No secrets management or sensitive data handling is required based on the current codebase.
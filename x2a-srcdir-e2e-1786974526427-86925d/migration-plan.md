# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a small Chef cookbook environment with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and limited dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, supported platforms, and version information. Will be replaced by Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains configuration attributes for Nginx. Will be migrated to Ansible role defaults.
- `recipes/default.rb`: Contains the main Chef recipe for Nginx installation and configuration. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation tasks
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management detected in the current codebase
- Standard service security practices should be implemented in the Ansible roles:
  - Firewall rules for Nginx (port 80) and Redis
  - Proper file permissions for web content

### Technical Challenges

- **Simple Migration**: The cookbooks are straightforward with minimal complexity, presenting no significant technical challenges
- **Attribute Translation**: Ensure Nginx attributes from Chef are properly mapped to Ansible variables

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation role with minimal complexity
2. **nginx role** (Priority 2): Nginx web server role that may have configuration options

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/   # Migrated from simple-nginx cookbook
│   │   ├── defaults/
│   │   │   └── main.yml  # From attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # From file resource in recipes/default.rb
│   │   └── meta/
│   │       └── main.yml  # From metadata.rb
│   └── redis_cache/  # Migrated from cache cookbook
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── meta/
│           └── main.yml  # From cookbooks/cache/metadata.rb
└── playbook.yml  # Main playbook to apply roles
```

### Assumptions

1. The Nginx configuration is minimal and doesn't require complex templating beyond what's shown in the recipes
2. Redis is used as a simple cache without custom configuration
3. No authentication or complex security requirements exist for either service
4. No environment-specific configurations are needed
5. The target systems will be Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata
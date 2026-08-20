# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook called "simple-nginx" and a local dependency cookbook called "cache". The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for this migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible role defaults/main.yml.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will be migrated to Ansible tasks/main.yml.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Will be replaced by Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credentials were detected in the repository
- Basic service configuration should follow Ansible security best practices

### Technical Challenges

- **Simple Migration**: The cookbooks are straightforward with minimal complexity, making this a low-risk migration
- **Dependency Management**: Ensure the relationship between the main role and the cache role is maintained in Ansible

### Migration Order

1. **cache cookbook** (Priority 1): Migrate first as it's a dependency of the main cookbook
   - Create an Ansible role for Redis installation and configuration
   - Test independently to ensure Redis is properly installed and running

2. **simple-nginx cookbook** (Priority 2): Migrate after the cache role is complete
   - Create an Ansible role for Nginx installation and configuration
   - Ensure proper dependency on the cache role
   - Test to verify Nginx is properly installed, running, and serving the welcome page

### Assumptions

1. The external nginx dependency is a standard Chef cookbook and doesn't contain custom modifications
2. No complex configuration templates are used (none were found in the repository)
3. No custom resources or libraries are used (none were found in the repository)
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7+
5. No special runtime requirements exist beyond what's explicitly defined in the cookbooks

## Implementation Plan

### Ansible Structure

```
ansible-project/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Will contain nginx configuration variables
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Migrated from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Dependencies and metadata
│   │   ├── tasks/
│   │   │   └── main.yml  # Migrated from recipes/default.rb
│   │   └── files/
│   │       └── index.html  # Welcome page content
│   └── redis_cache/
│       ├── meta/
│       │   └── main.yml  # Dependencies and metadata
│       └── tasks/
│           └── main.yml  # Migrated from cookbooks/cache/recipes/default.rb
└── playbook.yml  # Main playbook that includes both roles
```

### Timeline Estimate

- **Analysis and Planning**: 2 hours (completed)
- **Role Development**: 4 hours
  - Redis Cache Role: 1.5 hours
  - Nginx Role: 2.5 hours
- **Testing**: 2 hours
- **Documentation**: 1 hour
- **Total**: 9 hours (approximately 1-2 days of work)
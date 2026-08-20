# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation, service management, and content creation. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible nginx role or direct package installation tasks
- **cache (1.0.0)**: Migrate the local cache cookbook to Ansible tasks for Redis installation
- **redis-server**: Direct package installation via Ansible apt/yum module

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credentials or secrets management detected
- Standard service ports (80 for Nginx, default for Redis) should be reviewed for security during migration

### Technical Challenges

- **External nginx dependency**: The cookbook depends on an external 'nginx' cookbook that is declared but not included in the repository. The migration will need to implement equivalent functionality directly or through Ansible Galaxy roles.
- **Configuration management**: Ensure that Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with static content

### Assumptions

1. The external 'nginx' dependency is used for advanced configuration not visible in the current codebase
2. No custom templates or complex configurations are used beyond what's visible in the repository
3. No specific security hardening or custom configurations are required
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
5. No special handling for secrets or credentials is needed
6. Redis is used as a simple cache without complex configuration

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis/
│       └── tasks/
│           └── main.yml  # Converted from cache cookbook
└── site.yml  # Main playbook
```

## Migration Timeline

Given the simplicity of the codebase:
- Analysis and planning: 2 hours (completed)
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1-2 days)
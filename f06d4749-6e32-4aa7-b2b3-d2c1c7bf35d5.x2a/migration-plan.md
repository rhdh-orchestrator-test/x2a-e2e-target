# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on deploying Nginx with Redis caching. The codebase is relatively small, consisting of one main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for complete migration, testing, and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server deployment with basic configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains Nginx configuration attributes that should be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration, to be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx collection or create custom Nginx role
- **redis-server (unspecified version)**: Replace with Ansible community.redis collection or create custom Redis role

### Security Considerations

- No explicit security configurations identified in the current codebase
- Basic service security should be implemented in the Ansible roles:
  - Nginx: Configure proper TLS/SSL, remove server tokens, implement security headers
  - Redis: Password protection, network binding restrictions, firewall rules

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook that is declared but not included. The migration will need to either:
  1. Implement the missing functionality directly in Ansible
  2. Use the community.nginx collection as a replacement
  3. Determine what specific features from the external dependency were being used

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   ├── templates/
│   │   │   └── nginx.conf.j2
│   │   └── defaults/
│   │       └── main.yml
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── playbook.yml
```

### Assumptions

1. The cookbook is intended for basic Nginx deployment without complex configurations
2. Redis is used as a simple cache without advanced configuration
3. No specific security requirements are implemented in the current code
4. No custom templates or configurations beyond the basic package installation
5. No specific environment variables or secrets management
6. The external 'nginx' dependency may provide additional functionality not visible in the current codebase
7. No specific monitoring or logging requirements are defined

### Migration Tasks

1. Create Ansible roles for Nginx and Redis cache
2. Convert Chef attributes to Ansible variables
3. Convert Chef resources to Ansible tasks:
   - `package` resources → `ansible.builtin.package` or specific modules like `apt` or `yum`
   - `service` resources → `ansible.builtin.service`
   - `file` resources → `ansible.builtin.copy` or `ansible.builtin.template`
4. Implement proper variable templating for configuration files
5. Create a main playbook that includes both roles
6. Document the new Ansible structure and usage
7. Create tests to validate the migrated functionality
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. Based on the complexity and size, this migration could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation, service management, and basic content creation. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx tasks
- **cache (local)**: Convert to Ansible tasks for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management detected in the current codebase
- Standard service security practices should be implemented in the Ansible roles:
  - Firewall rules for Nginx (port 80) and Redis
  - Redis password protection (not implemented in the original cookbook)

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The Ansible migration will need to either incorporate this functionality directly or use an Ansible Galaxy role.
- **Configuration management**: Ensure Nginx configuration parameters from attributes are properly mapped to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The external 'nginx' dependency was used for advanced configuration not visible in the current codebase
2. No custom templates or additional files are used beyond what's visible in the repository
3. No complex conditionals or environment-specific configurations are present
4. No secrets management or security hardening is implemented in the current code
5. The cookbooks are designed for Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata files

## Ansible Structure Recommendation

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # Converted from file resource
│   │   └── defaults/
│   │       └── main.yml  # Converted from attributes/default.rb
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Default variables
└── playbook.yml  # Main playbook that includes both roles
```

## Migration Timeline

Given the small scope of this project:
- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1.5 days)
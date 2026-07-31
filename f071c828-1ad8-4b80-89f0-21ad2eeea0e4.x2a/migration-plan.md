# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook infrastructure focused on a simple Nginx web server setup with a Redis cache dependency. The migration scope is relatively small, with one main cookbook and one local dependency cookbook. Based on the repository analysis, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs and configures Nginx with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Will need to be translated to Ansible role metadata or collection dependencies.
- `attributes/default.rb`: Contains Nginx configuration attributes like port, user, and worker processes. Will need to be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Will need to be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management. Will need to be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible's `nginx` module or community.general collection
- **cache (1.0.0)**: Local dependency that installs Redis. Replace with Ansible Redis role or tasks

### Security Considerations

- No explicit security configurations were identified in the examined files
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **External Dependency Resolution**: The cookbook depends on an external 'nginx' cookbook that is declared but not included in the repository. The migration will need to determine if any specific configurations from this external dependency are required.
- **Attribute Translation**: Chef attributes will need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The external 'nginx' dependency is used only for installation and basic configuration, not for complex customizations
2. No additional Chef resources or custom logic exists beyond what's visible in the repository
3. No complex templating or configuration management is required
4. No integration with external systems or services beyond Redis
5. No specific security hardening or compliance requirements exist
6. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+

## Ansible Migration Details

### Proposed Ansible Structure

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Former Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Former Chef attributes
│   │   ├── tasks/
│   │   │   └── main.yml  # Former Chef recipes
│   │   └── meta/
│   │       └── main.yml  # Dependencies
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Former cache cookbook
│       └── meta/
│           └── main.yml  # Dependencies
└── site.yml  # Main playbook
```

### Implementation Notes

1. Convert Chef's package and service resources to Ansible's package and service modules
2. Convert file resource to Ansible's copy or template module
3. Move Chef attributes to Ansible variables in defaults/main.yml
4. Create a main playbook that includes both roles
5. Document any assumptions or manual steps required for the migration
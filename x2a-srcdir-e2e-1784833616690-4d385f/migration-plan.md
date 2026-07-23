# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook called `simple-nginx` that installs and configures Nginx with a simple welcome page. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with only two cookbooks to migrate: the main `simple-nginx` cookbook and its local dependency `cache` cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, configures it, and creates a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible metadata or requirements files.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be translated to Ansible variables.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `ansible-role-nginx` or use the built-in `nginx` module
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or credentials were found in the examined files
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
  - Firewall rules for Redis and Nginx services

### Technical Challenges

- **Attribute Translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults
- **Service Management**: Ensure proper idempotent service management in Ansible
- **Platform Support**: Maintain support for both Ubuntu and CentOS as specified in the original cookbooks

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration that depends on the cache role

### Assumptions

1. The external `nginx` dependency is used for advanced configurations not visible in the examined files
2. No custom templates or additional files are used beyond what was discovered
3. No complex Chef resources or custom resources are used
4. No secrets management or vault integration is required
5. The Redis configuration uses default settings without customization
6. The Nginx configuration is minimal and primarily uses default settings with only port, user, and worker_processes being configurable

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventories/
│   └── development/
│       ├── group_vars/
│       │   └── all.yml  # Variables from attributes/default.rb
│       └── hosts
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # From attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # From file resource in recipes/default.rb
│   └── redis/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml  # From cookbooks/cache/recipes/default.rb
├── site.yml  # Main playbook
└── requirements.yml  # External role dependencies
```

## Timeline Estimate

- Analysis and planning: 2 hours (completed)
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours
- Total: 12 hours (1.5 days)
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with basic settings. The migration scope is relatively small, consisting of one main cookbook with a local dependency on a `cache` cookbook that installs Redis. The migration complexity is low to moderate, with an estimated timeline of 1-2 days for complete conversion to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration values for Nginx (port, user, worker processes). These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `ansible.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No credentials or secrets management was detected
- Standard service security practices should be implemented in the Ansible roles

### Technical Challenges

- **External dependency handling**: The cookbook depends on an external 'nginx' cookbook that isn't included in the repository. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration management**: Ensure that all Chef attributes are properly mapped to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Convert to an Ansible role first as it's a dependency for the main cookbook
2. **simple-nginx cookbook** (Priority 2): Convert to an Ansible role after the cache role is complete

### Ansible Structure Recommendation

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
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # From file resource in recipes/default.rb
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Any default variables
├── site.yml  # Main playbook
└── requirements.yml  # External role dependencies
```

### Assumptions

1. The cookbook is intended for basic Nginx installation without complex configurations
2. Redis is used as a simple cache without custom configurations
3. No specific security requirements beyond default service configurations
4. No custom templates or complex file manipulations are needed
5. The external 'nginx' dependency provides standard Nginx functionality that can be replaced with Ansible's built-in modules or Galaxy roles
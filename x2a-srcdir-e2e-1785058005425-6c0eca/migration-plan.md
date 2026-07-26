# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook called "simple-nginx" that installs and configures Nginx with basic settings. The migration scope is relatively small, consisting of one main cookbook with a local dependency cookbook called "cache" that installs Redis. The migration complexity is low to moderate, with an estimated timeline of 1-2 days for complete conversion to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains default attributes for Nginx configuration (port, user, worker processes)
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation
- **cache (local)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Basic service configuration without SSL/TLS settings

### Technical Challenges

- **External dependency**: The cookbook depends on an external 'nginx' cookbook that is declared but not included in the repository. The Ansible migration will need to implement the functionality that would have been provided by this external dependency.
- **Attribute mapping**: Chef attributes need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration

### Assumptions

1. The external 'nginx' dependency provides additional configuration beyond what's visible in the simple-nginx cookbook
2. No complex templating or conditional logic exists in the current implementation
3. No specific security hardening or custom configurations are required
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
5. No integration with external monitoring or logging systems is required
6. No specific user management or permissions beyond basic service configuration is needed

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Port, user, worker_processes variables
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation and configuration
│   │   └── templates/
│   │       └── index.html.j2  # Welcome page template
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Redis installation and service management
│       └── defaults/
│           └── main.yml  # Redis configuration variables
└── site.yml  # Main playbook
```

## Migration Timeline

- **Analysis and Planning**: 2 hours (completed)
- **Role Development**: 4 hours
- **Testing**: 4 hours
- **Documentation**: 2 hours
- **Total Estimated Time**: 12 hours (1.5 days)
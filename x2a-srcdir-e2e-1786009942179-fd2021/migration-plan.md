# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for deploying Nginx with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external)
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index page

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Create an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Consider implementing TLS/SSL for Nginx in the Ansible role

### Technical Challenges

- **Attribute Translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables
- **Service Management**: Ensure proper service management for both Nginx and Redis in Ansible

### Migration Order

1. **cache role** (Priority 1): Create Ansible role for Redis installation and configuration
2. **nginx role** (Priority 2): Create Ansible role for Nginx installation and configuration

### Assumptions

1. The external 'nginx' dependency is used for additional Nginx configuration not visible in the current codebase
2. The cookbook is intended for basic web server setup without complex configurations
3. No custom templates or additional files are used beyond what's visible in the repository
4. No specific security requirements or hardening is implemented in the current setup
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+

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
│   │   │   └── main.yml  # Install nginx, configure service, create index
│   │   ├── templates/
│   │   │   └── index.html.j2  # Template for index page
│   │   └── defaults/
│   │       └── main.yml  # Default variables (port, user, worker_processes)
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Install redis, configure service
│       └── defaults/
│           └── main.yml  # Default variables
└── playbook.yml  # Main playbook applying both roles
```

## Migration Timeline

- **Analysis & Planning**: 2 hours (completed)
- **Role Development**: 4 hours
- **Testing**: 2 hours
- **Documentation**: 2 hours
- **Total Estimated Time**: 10 hours (1-2 days)
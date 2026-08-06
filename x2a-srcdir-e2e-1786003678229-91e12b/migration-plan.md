# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook called "simple-nginx" that installs and configures Nginx with basic settings. The migration scope is relatively small, consisting of one main cookbook with a local dependency cookbook called "cache" that installs Redis. The migration complexity is low to moderate, with an estimated timeline of 1-2 days for complete conversion to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs the web server with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Convert dependencies to Ansible Galaxy requirements.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Migration consideration: Convert to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. Migration consideration: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook. Migration consideration: Include in Ansible Galaxy requirements.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis. Migration consideration: Convert to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (explicitly specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` module or community.general collection
- **redis-server (unspecified version)**: Replace with Ansible's `apt`/`yum` module for installation and `service` module for management

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Basic service configuration should maintain default security settings

### Technical Challenges

- **External dependency handling**: The cookbook depends on an external 'nginx' cookbook that is not included in the repository. The Ansible migration will need to implement all necessary Nginx configurations directly rather than relying on external dependencies.
- **Platform compatibility**: The cookbook supports both Ubuntu and CentOS. Ansible playbooks should maintain this compatibility using conditional tasks based on the OS family.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, service management, and content creation

### Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventories/
│   └── development/
│       ├── hosts
│       └── group_vars/
│           └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # From attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # From file resource in recipes/default.rb
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Any default variables
├── playbook.yml  # Main playbook that includes roles
└── requirements.yml  # Any external role dependencies
```

### Assumptions

1. The cookbook is intended for basic Nginx installation without complex configurations
2. Redis is used as a simple cache without custom configurations
3. No specific Nginx modules or advanced features are required
4. No specific Redis configuration beyond the default installation is needed
5. No authentication or security hardening is implemented in the current cookbooks
6. The external 'nginx' dependency might contain configurations not visible in this repository
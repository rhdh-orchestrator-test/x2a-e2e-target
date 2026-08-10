# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook with one local dependency cookbook. Based on the limited complexity, this migration can likely be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs and configures Nginx with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. Will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. Will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Standard service security practices should be implemented in the Ansible roles:
  - Firewall rules for Nginx (port 80) and Redis
  - Redis access control configuration

### Technical Challenges

- **External dependency handling**: The 'nginx' cookbook is referenced but not included in the repository. The Ansible migration will need to either incorporate the functionality directly or use a community role.
- **Configuration management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content deployment

### Ansible Structure Recommendation

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
│   │   │   └── main.yml  # Default variables from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Based on metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Logic from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Template for the index page
│   └── redis_cache/
│       ├── meta/
│       │   └── main.yml  # Based on cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Logic from cache/recipes/default.rb
└── site.yml  # Main playbook that applies roles
```

### Assumptions

1. The cookbook is intended for a simple web server setup with Redis caching
2. No complex configuration or customization is required for either Nginx or Redis
3. No specific security requirements beyond standard practices
4. No specific performance tuning requirements
5. The external 'nginx' dependency likely provides additional configuration options not visible in this repository
6. No specific backup or monitoring requirements were identified
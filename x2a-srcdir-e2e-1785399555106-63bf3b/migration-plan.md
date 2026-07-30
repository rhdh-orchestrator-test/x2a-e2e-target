# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with a local cache dependency. The migration scope is relatively small, consisting of one main cookbook and one local dependency cookbook. Based on the repository analysis, this is a straightforward migration that could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
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
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. This should be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This should be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in the metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx tasks
- **cache (local)**: Convert to Ansible tasks for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the repository
- No credential patterns or secrets management were detected
- Consider implementing TLS/SSL for Nginx in the Ansible role

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The Ansible migration will need to either incorporate this functionality directly or use an Ansible Galaxy role.
- **Configuration management**: Ensure that the Nginx configuration attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Convert the Redis installation and configuration to Ansible tasks
2. **simple-nginx cookbook** (Priority 2): Convert the Nginx installation, service management, and content creation to Ansible tasks

### Ansible Structure Recommendation

```
ansible-nginx/
├── defaults/
│   └── main.yml           # Variables from attributes/default.rb
├── tasks/
│   ├── main.yml           # Main tasks from recipes/default.rb
│   └── cache.yml          # Redis tasks from cookbooks/cache/recipes/default.rb
├── templates/
│   └── index.html.j2      # Template for the index page
├── meta/
│   └── main.yml           # Role metadata
└── README.md              # Documentation
```

### Assumptions

1. The cookbook is intended for a simple Nginx deployment with Redis caching
2. No complex configuration or customization is required
3. The external 'nginx' dependency is used for additional Nginx configuration not present in the repository
4. No specific security requirements or hardening is needed
5. No specific performance tuning is required
6. The cookbook is designed to work on Ubuntu 18.04+ or CentOS 7.0+
7. No specific user management or permissions beyond default are required
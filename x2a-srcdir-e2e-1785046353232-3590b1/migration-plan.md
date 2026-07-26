# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook with one local dependency cookbook. Based on the complexity and size, this migration could be completed in approximately 1-2 days by a single engineer familiar with both Chef and Ansible.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. Will need to be translated to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index.html file.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and starts Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: The cookbooks support Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the metadata.rb files.
- **Virtual Machine Technology**: Not specified in the repository.
- **Cloud Platform**: Not specified in the repository.

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks.
- No secrets management or credential patterns were detected.
- Standard service ports are used (port 80 for Nginx).

### Technical Challenges

- **External Dependencies**: The cookbook depends on an external 'nginx' cookbook that is not included in the repository. The Ansible migration will need to either incorporate the functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content deployment

### Assumptions

1. The external 'nginx' dependency provides standard Nginx installation and configuration capabilities.
2. No complex templating or custom configurations are being used beyond what is visible in the repository.
3. No specific security hardening or custom configurations are required beyond the basic installation.
4. The welcome page content is static and doesn't require dynamic content generation.
5. No specific user management or permissions beyond the default 'www-data' user are required.
6. No SSL/TLS configuration is present in the current implementation.

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventories/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # Converted from file resource
│   │   └── meta/
│   │       └── main.yml  # Converted from metadata.rb
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── meta/
│           └── main.yml  # Converted from cookbooks/cache/metadata.rb
└── site.yml  # Main playbook that includes both roles
```

## Timeline Estimate

- **Analysis and Planning**: 2 hours (completed)
- **Role Development**: 4 hours
  - Redis Cache Role: 1 hour
  - Nginx Role: 3 hours
- **Testing**: 2 hours
- **Documentation**: 1 hour
- **Total**: 9 hours (approximately 1-2 days)
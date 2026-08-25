# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with a simple cache dependency. The migration scope is relatively small, consisting of one main cookbook with one local dependency cookbook. Based on the complexity and size, this migration should be straightforward and could be completed within 1-2 days by a single developer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx role or create a custom Nginx role
- **redis-server (unspecified version)**: Replace with community.redis role or create a custom Redis role

### Security Considerations

- No explicit security configurations were identified in the cookbook
- No secrets management or credential patterns were detected
- Basic service configuration should maintain default security settings

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook that is declared but not included in the repository. The migration will need to determine what functionality from this external dependency is actually used.
- **Configuration Management**: Ensure that Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, depends on cache

### Assumptions

1. The external 'nginx' dependency is only used for basic installation and configuration, not for complex custom configurations.
2. No custom templates or additional files are used beyond what was discovered in the repository.
3. No complex conditionals or platform-specific code exists in the recipes.
4. No authentication or authorization mechanisms are implemented.
5. No custom error pages or advanced Nginx configurations are required.
6. The Redis cache is a standalone service and not configured for clustering or replication.

## Ansible Migration Details

### Proposed Ansible Structure

```
simple-nginx/
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
│   │       └── main.yml  # Default variables
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Default variables
└── site.yml  # Main playbook
```

### Timeline Estimate

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 2 hours
- Documentation: 2 hours
- Total: 10 hours (1-2 days)
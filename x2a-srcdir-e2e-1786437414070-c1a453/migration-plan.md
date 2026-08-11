# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

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
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Should be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx tasks
- **cache (1.0.0)**: Migrate the local cache cookbook to Ansible tasks for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Standard service security should be implemented in the Ansible roles:
  - Nginx: Configure proper file permissions, disable unnecessary modules
  - Redis: Configure authentication, bind to appropriate interfaces

### Technical Challenges

- **Dependency Management**: The original cookbook relies on an external 'nginx' dependency that is declared but not included. The migration will need to either:
  1. Use an Ansible Galaxy role for Nginx
  2. Implement custom Nginx tasks based on the expected functionality

- **Configuration Translation**: Convert Chef attributes to Ansible variables, ensuring proper templating and defaults

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with dependency on cache

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # From the static HTML content
│   │   └── defaults/
│   │       └── main.yml  # Default variables
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── playbook.yml  # Main playbook applying the roles
```

### Assumptions

1. The external 'nginx' dependency was used for advanced configurations not present in the simple cookbook
2. No custom templates or configurations beyond what's visible in the repository
3. No complex conditionals or platform-specific code in the recipes
4. No secrets management or security hardening in the original cookbooks
5. The Redis cache is a standalone service and not configured for clustering
6. The Nginx configuration is minimal and doesn't require extensive customization
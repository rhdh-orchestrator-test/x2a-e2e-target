# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook called "simple-nginx" that installs and configures Nginx with basic settings. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with only two cookbooks to migrate (simple-nginx and cache). Based on the complexity and size, this migration should be straightforward and could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs the web server, ensures it's running, and creates a basic index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, supported platforms, and version information. Will be replaced by Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible role defaults/main.yml.
- `recipes/default.rb`: Contains the main recipe for installing Nginx, starting the service, and creating a basic index page. Will be migrated to Ansible tasks/main.yml.
- `cookbooks/cache/metadata.rb`: Defines metadata for the cache cookbook. Will be replaced by Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible's `nginx` module or community.general collection
- **cache (1.0.0)**: Local cookbook dependency that installs Redis, replace with Ansible Redis role or tasks
- **redis-server**: Package dependency, use Ansible's package module

### Security Considerations

- No explicit security configurations identified in the current codebase
- Basic file permissions are set for the index.html file (0644)
- No credentials or secrets management detected
- No SSL/TLS configuration present

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collections.
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables with appropriate scoping (defaults, vars, group_vars, etc.)

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The external nginx dependency is a standard community cookbook with no custom modifications
2. No complex Chef-specific features (like search, data bags, environments) are being used
3. No custom templates or additional files beyond what's visible in the repository
4. No integration with external systems or services beyond basic package installation
5. The target environment will continue to support Ubuntu 18.04+ and CentOS 7.0+

## Ansible Structure Recommendation

```
ansible-simple-nginx/
├── collections/
│   └── requirements.yml  # For community.general if needed
├── inventory/
│   └── hosts             # Target hosts inventory
├── roles/
│   ├── cache/            # Migrated from cookbooks/cache
│   │   ├── defaults/
│   │   │   └── main.yml  # Default variables
│   │   ├── meta/
│   │   │   └── main.yml  # Role metadata
│   │   └── tasks/
│   │       └── main.yml  # Redis installation tasks
│   └── nginx/            # Migrated from root cookbook
│       ├── defaults/
│       │   └── main.yml  # Converted from attributes/default.rb
│       ├── meta/
│       │   └── main.yml  # Role metadata
│       └── tasks/
│           └── main.yml  # Nginx installation tasks
└── site.yml              # Main playbook
```

## Migration Timeline

Given the small scope and low complexity:
- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1.5 days)
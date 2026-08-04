# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role from Ansible Galaxy or create a custom role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management identified in the current codebase
- Basic service configuration should maintain default security settings
- No SSL/TLS configurations present in the current implementation

### Technical Challenges

- **Attribute Translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables
- **Service Management**: Chef service resources need to be translated to Ansible service modules
- **File Content Management**: Chef file resources need to be translated to Ansible template or copy modules

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service configuration
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Structure Recommendation

```
ansible-nginx/
├── defaults/
│   └── main.yml       # Variables from Chef attributes
├── tasks/
│   └── main.yml       # Tasks from Chef recipes
├── templates/
│   └── index.html.j2  # Template for index.html
└── meta/
    └── main.yml       # Role metadata

ansible-redis-cache/
├── tasks/
│   └── main.yml       # Redis installation and service tasks
└── meta/
    └── main.yml       # Role metadata
```

### Assumptions

1. The Chef cookbook is designed for a simple Nginx web server with Redis caching
2. No complex configurations or customizations are present
3. No secrets management or security hardening is implemented
4. The cookbook is intended for Ubuntu 18.04+ or CentOS 7.0+ environments
5. The Nginx configuration is minimal with only basic settings defined in attributes
6. No custom templates or additional files beyond what's visible in the repository
7. No complex dependency resolution or version pinning requirements
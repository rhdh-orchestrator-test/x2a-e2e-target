# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with basic settings. The migration scope is relatively small, consisting of one main cookbook with a local dependency cookbook called `cache`. The migration complexity is low to moderate, with an estimated timeline of 1-2 days for complete conversion to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, configures basic settings, and creates a default index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Defines default attributes for Nginx configuration
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Consider implementing TLS/SSL for Nginx in the Ansible role

### Technical Challenges

- **Attribute Translation**: Convert Chef attributes to Ansible variables
  - Nginx port, user, and worker_processes attributes need to be mapped to Ansible variables
- **Service Management**: Ensure proper service management in Ansible for both Nginx and Redis

### Migration Order

1. **cache cookbook** (Priority 1): Convert to Ansible role first as it's a dependency
   - Create `roles/redis_cache` with tasks for package installation and service management
   - Define default variables based on the original cookbook

2. **simple-nginx cookbook** (Priority 2): Convert main cookbook to Ansible role
   - Create `roles/nginx_web` with tasks for package installation, service management, and content creation
   - Define variables based on the original attributes

### Assumptions

1. The cookbook is used in a simple deployment scenario without complex configurations
2. No custom templates or additional files are used beyond what's visible in the repository
3. No specific security requirements or hardening is needed
4. The external nginx dependency provides standard Nginx functionality
5. No specific configuration is required for Redis beyond basic installation and service enablement
6. No backup or monitoring configurations are present in the current implementation

## Implementation Plan

### Ansible Structure

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── nginx_web/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis_cache/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
└── playbook.yml
```

### Timeline Estimate

- Analysis and planning: 2 hours (completed)
- Role development: 4 hours
- Testing: 2 hours
- Documentation: 2 hours
- Total: 1 day (8 hours)

### Testing Strategy

1. Develop Ansible roles locally
2. Test with Vagrant or Docker containers
3. Verify functionality matches original Chef cookbook behavior
4. Document any differences or improvements
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called "simple-nginx" that installs and configures Nginx web server with a basic configuration. The cookbook follows a metadata-only dependency strategy and includes a local dependency on a "cache" cookbook that installs Redis. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static index page creation

- **cache**:
    - Description: Simple Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible metadata in roles or collections.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Will be replaced by Ansible metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or direct package installation using the `apt` or `yum` module
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic service security should be implemented in the Ansible roles:
  - Firewall rules for Nginx and Redis
  - Secure default configurations

### Technical Challenges

- **Simple Migration**: The cookbooks are straightforward with minimal complexity, presenting no significant technical challenges
- **Dependency Management**: The external nginx dependency will need to be replaced with appropriate Ansible modules or roles

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The cookbooks are used in a simple environment without complex integrations
2. No custom templates or configurations beyond what's visible in the repository
3. No specific performance tuning or advanced configurations for either Nginx or Redis
4. No authentication or TLS/SSL configuration for Nginx
5. Redis is used with default configuration without authentication
6. The external nginx dependency is used only for basic installation and not for complex configurations

## Migration Implementation Details

### Ansible Structure

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   └── tasks/
│   │       └── main.yml
│   └── redis/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml
└── site.yml
```

### Variable Mapping

Chef attributes to Ansible variables:
- `default['nginx']['port']` → `nginx_port`
- `default['nginx']['user']` → `nginx_user`
- `default['nginx']['worker_processes']` → `nginx_worker_processes`

### Task Mapping

1. **Redis Installation (from cache cookbook)**:
   - Use Ansible's `package` module to install redis-server
   - Use Ansible's `service` module to enable and start redis-server

2. **Nginx Installation**:
   - Use Ansible's `package` module to install nginx
   - Use Ansible's `service` module to enable and start nginx
   - Use Ansible's `copy` module to create the index.html file

### Timeline Estimate

Given the simplicity of the cookbooks:
- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1-2 days)
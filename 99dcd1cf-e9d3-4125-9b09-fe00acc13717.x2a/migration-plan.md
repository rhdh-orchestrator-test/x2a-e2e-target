# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` with a local dependency on a `cache` cookbook. The primary cookbook installs and configures Nginx web server, while the cache cookbook installs Redis as a caching solution. The migration scope is relatively small, with only two cookbooks to migrate. Given the simplicity of the cookbooks, this migration should be straightforward and could be completed within 1-2 days by a single developer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, supported platforms, and version information. Will be replaced by Ansible role metadata in `meta/main.yml`.
- `attributes/default.rb`: Contains default configuration values for Nginx. Will be migrated to Ansible role defaults in `defaults/main.yml`.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Will be migrated to Ansible tasks in `tasks/main.yml`.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook. Will be replaced by Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and configuration. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` module or community.general collection
- **cache (local)**: Migrate to a separate Ansible role for Redis installation

### Security Considerations

- No explicit security configurations were identified in the current cookbooks
- No secrets management or credential patterns were detected
- Basic service security should be implemented in the Ansible roles:
  - Firewall rules for Nginx and Redis
  - Proper file permissions for configuration files

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. In Ansible, we'll need to handle role dependencies through:
  - Role dependencies in `meta/main.yml`
  - Collection requirements in `requirements.yml`

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation role with minimal complexity
2. **nginx role** (Priority 2): Nginx web server role that depends on the cache role

### Ansible Structure

The proposed Ansible structure will be:

```
ansible-simple-nginx/
├── collections/
│   └── requirements.yml  # For external collection dependencies
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Migrated from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Migrated from metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Migrated from recipes/default.rb
│   │   └── templates/
│   │       └── nginx.conf.j2  # New template for configuration
│   └── redis_cache/
│       ├── meta/
│       │   └── main.yml  # Migrated from cookbooks/cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Migrated from cookbooks/cache/recipes/default.rb
└── playbook.yml  # Main playbook that applies both roles
```

### Migration Tasks

1. **Create Ansible Role Structure**:
   - Create directory structure for both roles
   - Set up metadata files with dependencies

2. **Migrate Nginx Configuration**:
   - Convert attributes to Ansible variables
   - Convert package and service resources to Ansible modules
   - Create templates for configuration files

3. **Migrate Redis Cache Configuration**:
   - Convert package and service resources to Ansible modules
   - Add proper Redis configuration

4. **Create Main Playbook**:
   - Define host groups
   - Apply roles in the correct order

5. **Testing**:
   - Test each role individually
   - Test the complete playbook

### Assumptions

- The external nginx dependency is a standard Chef cookbook with no custom modifications
- No complex Chef resources or Ruby code is used in the recipes
- No custom templates or files are required beyond what's visible in the repository
- The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
- No special configuration is needed for Redis beyond basic installation
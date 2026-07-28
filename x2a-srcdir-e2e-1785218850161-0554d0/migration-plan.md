# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` that installs and configures Nginx with basic settings. The cookbook follows a metadata-only dependency strategy and includes one local dependency (`cache` cookbook) and one external dependency (`nginx` cookbook). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static index page creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible metadata in `meta/main.yml`.
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

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (1.0.0)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **External Dependencies**: The `nginx` cookbook is referenced but not included. Need to determine if any specific configurations from this cookbook are required.
- **Service Configuration**: Ensure proper service management for both Nginx and Redis in Ansible.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation and basic configuration

### Assumptions

1. The cookbook is used for basic Nginx installation without complex configurations
2. Redis is used as a simple cache without custom configurations
3. No templates or custom configurations are used beyond what's visible in the repository
4. No secrets or sensitive data management is required
5. The external `nginx` dependency is used only for basic installation and not for complex configurations
6. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
7. No specific performance tuning or security hardening is implemented in the current cookbooks

## Migration Implementation Plan

### For the cache role:

1. Create an Ansible role structure:
   ```
   roles/cache/
     tasks/main.yml
     meta/main.yml
   ```

2. Implement Redis installation and service management in `tasks/main.yml`

### For the nginx role:

1. Create an Ansible role structure:
   ```
   roles/nginx/
     tasks/main.yml
     vars/main.yml
     meta/main.yml
     files/index.html
   ```

2. Migrate attributes to `vars/main.yml`
3. Implement Nginx installation, configuration, and service management in `tasks/main.yml`
4. Create a static index.html file in `files/`

### Playbook Structure:

Create a main playbook that includes both roles:

```yaml
---
- hosts: web_servers
  roles:
    - cache
    - nginx
```

## Testing Strategy

1. Create a test environment with Ubuntu 18.04 or CentOS 7
2. Run the Ansible playbook against the test environment
3. Verify Nginx is installed and running on port 80
4. Verify the index page is accessible
5. Verify Redis is installed and running
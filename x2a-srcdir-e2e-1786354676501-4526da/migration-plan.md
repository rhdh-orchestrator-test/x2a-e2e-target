# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named 'simple-nginx' that installs and configures Nginx with a simple welcome page. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with one main cookbook and one local dependency cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

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

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible metadata in galaxy.yml.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Will be replaced by Ansible metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or direct package installation using the `apt` or `yum` module
- **cache (local, v1.0.0)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- Default Nginx configuration should be reviewed for security best practices during migration
- Redis server in the cache cookbook should be configured with proper security settings (password, network binding, etc.)

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or by including the necessary roles directly.
- **Platform Support**: The cookbook supports both Ubuntu and CentOS. The Ansible playbooks should maintain this cross-platform compatibility using conditional tasks based on the ansible_os_family variable.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and configuration, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Ansible Structure Recommendation

```
simple-nginx/
├── galaxy.yml                  # Metadata for the collection
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml        # Variables (from attributes/default.rb)
│   │   ├── tasks/
│   │   │   └── main.yml        # Tasks (from recipes/default.rb)
│   │   └── meta/
│   │       └── main.yml        # Role metadata
│   └── cache/
│       ├── tasks/
│       │   └── main.yml        # Redis installation tasks
│       └── meta/
│           └── main.yml        # Role metadata
├── playbooks/
│   └── site.yml                # Main playbook that includes both roles
└── README.md                   # Documentation
```

### Assumptions

1. The external nginx dependency does not contain custom configurations that would need to be migrated
2. The Redis configuration in the cache cookbook is using default settings without customization
3. No secrets or sensitive data management is required for this migration
4. No complex conditionals or platform-specific code exists beyond what's visible in the examined files
5. No custom templates or files are being used beyond the simple index.html content created directly in the recipe
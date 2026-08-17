# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named 'simple-nginx' that installs and configures Nginx with a simple welcome page. The cookbook follows a metadata-only dependency strategy and includes a local dependency on a 'cache' cookbook that installs Redis. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx web server, configures basic settings, and creates a welcome page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, supported platforms, and version information. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be converted to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines metadata for the cache cookbook. Will need to be translated to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version not specified)**: Replace with Ansible's `nginx` module or community.general collection
- **redis-server (version not specified)**: Replace with Ansible's `apt`/`yum` modules for installation and `service` module for management

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic service security should be implemented in the Ansible roles:
  - Nginx: Configure proper file permissions for web content
  - Redis: Implement password protection and network binding restrictions

### Technical Challenges

- **Simple Configuration**: The cookbooks are straightforward with minimal complexity, presenting few migration challenges
- **Dependency Management**: The external 'nginx' dependency is declared but not included. The Ansible migration should include all necessary tasks rather than relying on external dependencies.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content creation

### Assumptions

1. The cookbooks are designed for Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata
2. The nginx cookbook is intended to be a simple web server with minimal configuration
3. The cache cookbook is intended to provide Redis as a caching layer
4. No complex configurations or customizations are required beyond what's explicitly defined in the recipes
5. No authentication or security measures are implemented in the current configuration
6. The external 'nginx' dependency is not critical for functionality as the cookbook implements its own nginx installation

## Ansible Migration Structure

The proposed Ansible structure will consist of:

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Converted from metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Template for the welcome page
│   └── cache/
│       ├── meta/
│       │   └── main.yml  # Converted from cookbooks/cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
└── site.yml  # Main playbook that includes both roles
```

This structure maintains separation of concerns while providing a clean migration path from the Chef cookbooks to Ansible roles.
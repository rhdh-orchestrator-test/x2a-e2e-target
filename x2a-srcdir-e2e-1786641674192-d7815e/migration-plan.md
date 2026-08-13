# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named 'simple-nginx' that installs and configures Nginx with a basic configuration. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with one main cookbook and one local dependency cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will require mapping these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. These will be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx collection or a custom Nginx role
- **cache (1.0.0)**: Migrate the local cache cookbook to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook which is not included in the repository. The migration will need to either:
  1. Implement Nginx configuration directly in Ansible
  2. Use the community.nginx collection
  3. Create a custom Nginx role based on the expected behavior

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content deployment

### Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # From file resource in recipes/default.rb
│   │   └── defaults/
│   │       └── main.yml  # From attributes/default.rb
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Any default variables
└── site.yml  # Main playbook
```

### Assumptions

1. The external 'nginx' cookbook is used only for basic Nginx installation and not for complex configurations
2. The Redis configuration in the cache cookbook uses default settings with no customization
3. No complex Chef-specific features (like search, data bags, or environments) are being used
4. No authentication or TLS/SSL configurations are required for either Nginx or Redis
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
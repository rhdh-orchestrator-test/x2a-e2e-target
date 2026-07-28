# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external)
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for installing Nginx, starting the service, and creating a basic index page
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation task
- **cache (local)**: Migrate to Ansible tasks for Redis installation and configuration
- **redis-server**: Direct package installation in Ansible

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
- Vault/secrets management:
  - No credentials or secrets detected in the current codebase

### Technical Challenges

- **Simple Migration**: The cookbook functionality is straightforward with minimal complexity
- **Attribute Translation**: Convert Chef attributes to Ansible variables
  - nginx.port → nginx_port
  - nginx.user → nginx_user
  - nginx.worker_processes → nginx_worker_processes

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 1): Nginx installation, configuration, and basic content

### Ansible Structure Recommendation

```
ansible/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation and configuration
│   │   └── templates/
│   │       └── index.html.j2  # Welcome page template
│   └── redis/
│       └── tasks/
│           └── main.yml  # Redis installation and configuration
└── site.yml  # Main playbook
```

### Assumptions

1. The current Chef implementation is complete and functional as-is
2. No complex configuration beyond what's visible in the codebase
3. No external dependencies beyond the declared 'nginx' cookbook
4. No specific security requirements or hardening needed
5. No custom templates or additional files beyond what's visible
6. No specific environment variables or runtime configurations required
7. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
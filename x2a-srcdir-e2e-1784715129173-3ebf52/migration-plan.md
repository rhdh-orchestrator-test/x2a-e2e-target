# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook called `simple-nginx` that installs and configures Nginx with basic settings, along with a local dependency cookbook called `cache` that installs Redis. The migration scope is relatively small, consisting of two cookbooks with simple configurations. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates a basic index page
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and starts Redis server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible's `nginx` role or direct package installation using the `apt`/`yum` module
- **cache (1.0.0)**: Migrate the Redis installation and configuration to Ansible tasks using the `apt`/`yum` module and service module

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credentials were detected
- Standard service ports are used (port 80 for Nginx)
- Vault/secrets management: No credentials detected in any module

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook which is not included in the repository. The Ansible migration will need to implement the functionality directly rather than relying on this dependency.
- **Configuration Management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1, low complexity): Migrate the Redis installation and service management
2. **simple-nginx cookbook** (Priority 2, moderate complexity): Migrate the Nginx installation, configuration, and index page creation

### Assumptions

1. The external 'nginx' cookbook is used for additional configuration not visible in the current repository
2. The cookbook is designed for Ubuntu 18.04+ or CentOS 7.0+ environments
3. No complex templating or configuration is required beyond what's visible in the repository
4. No custom Nginx configuration files are being managed
5. No SSL/TLS configuration is required
6. The Redis server is used as a simple cache without custom configuration

## Ansible Migration Details

### Proposed Structure

```
simple-nginx/
├── defaults/
│   └── main.yml  # Variables from attributes/default.rb
├── tasks/
│   └── main.yml  # Main tasks from recipes/default.rb
├── meta/
│   └── main.yml  # Metadata from metadata.rb
└── README.md

redis-cache/
├── tasks/
│   └── main.yml  # Tasks from cookbooks/cache/recipes/default.rb
├── meta/
│   └── main.yml  # Metadata from cookbooks/cache/metadata.rb
└── README.md
```

### Implementation Notes

1. Convert Chef attributes to Ansible variables
2. Replace Chef resources with equivalent Ansible modules:
   - `package` resource → `apt`/`yum` module
   - `service` resource → `service` module
   - `file` resource → `copy` or `template` module
3. Create a playbook that includes both roles in the correct order
4. Document any assumptions or manual steps required

The migration is straightforward due to the simplicity of the cookbooks and should be completed quickly with minimal risk.
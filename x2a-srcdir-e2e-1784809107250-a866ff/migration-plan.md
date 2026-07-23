# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with a simple welcome page. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with only two cookbooks to migrate: the main `simple-nginx` cookbook and its local dependency `cache` cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, configures it, and creates a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including name, version, dependencies, and supported platforms
- `attributes/default.rb`: Defines default attributes for Nginx configuration (port, user, worker processes)
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a welcome page
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module to install Nginx and the `ansible.builtin.template` module to configure it
- **cache (local)**: Migrate to an Ansible role that installs and configures Redis using the `ansible.builtin.package` and `ansible.builtin.service` modules

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Consider implementing TLS/SSL for Nginx in the Ansible role as a security enhancement

### Technical Challenges

- **External dependency handling**: The `nginx` dependency is declared but not included in the repository. The Ansible migration will need to either incorporate Nginx configuration directly or create a separate Ansible role for it.
- **Attribute management**: Chef attributes need to be converted to Ansible variables, which can be defined in `defaults/main.yml` or `vars/main.yml` within the role structure.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and configuration, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The cookbook is used in a simple environment without complex orchestration or integration with other systems
2. No custom templates or additional files are used beyond what's visible in the repository
3. The external `nginx` dependency is used for additional Nginx configuration not visible in the current cookbook
4. No specific security requirements or hardening is needed beyond basic installation
5. The welcome page content is static and doesn't require dynamic content generation
6. No specific performance tuning or advanced configuration is required for either Nginx or Redis

## Ansible Structure Recommendation

```
ansible-nginx/
├── defaults/
│   └── main.yml           # Default variables (port, user, worker_processes)
├── tasks/
│   └── main.yml           # Installation and configuration tasks
├── templates/
│   └── index.html.j2      # Template for welcome page
├── meta/
│   └── main.yml           # Role metadata
└── README.md              # Documentation

ansible-cache/
├── tasks/
│   └── main.yml           # Redis installation and configuration
├── meta/
│   └── main.yml           # Role metadata
└── README.md              # Documentation
```

## Migration Timeline

- Repository analysis and planning: 2 hours
- Development of Ansible roles: 4-6 hours
- Testing and validation: 2-4 hours
- Documentation: 1-2 hours
- Total estimated time: 1-2 days
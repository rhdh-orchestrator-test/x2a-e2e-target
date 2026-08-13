# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with basic settings. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with one main cookbook and one local dependency cookbook. Based on the complexity and size, this migration can be completed in approximately 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs the web server, configures basic settings, and creates a default index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` module or use the `package` module to install Nginx
- **cache (1.0.0)**: Local dependency that installs Redis. Convert to Ansible tasks using the `package` module for Redis installation and the `service` module for service management

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic service configuration should follow Ansible security best practices

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook that is not included in the repository. The migration will need to:
  1. Determine what functionality from the external nginx cookbook is being used
  2. Implement equivalent functionality directly in Ansible or use Ansible Galaxy roles

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The external 'nginx' dependency is used only for basic Nginx installation and configuration, which can be directly implemented in Ansible
2. No complex templating or configuration management is required beyond what's visible in the repository
3. No custom resources or libraries are being used
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
5. No specific performance tuning or advanced configurations are needed for Nginx or Redis

## Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis_cache/
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
└── site.yml  # Main playbook that includes both roles
```

## Timeline Estimate

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours
- Total: 12 hours (1-2 days)
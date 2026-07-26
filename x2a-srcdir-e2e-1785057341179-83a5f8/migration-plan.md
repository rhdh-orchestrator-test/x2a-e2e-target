# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with a Redis cache dependency. The migration scope is relatively small, consisting of one main cookbook with one local dependency cookbook. Based on the complexity and size, this migration can be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: ./ (root cookbook)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation for caching functionality
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains Nginx configuration parameters that should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation, service management, and content creation.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or direct package installation using the `apt` or `yum` module
- **cache (local)**: Migrate the Redis server installation to Ansible tasks using the `apt` or `yum` module and service management

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No credentials or secrets management was detected
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions

### Technical Challenges

- **External dependency handling**: The cookbook depends on an external 'nginx' cookbook that isn't included in the repository. The Ansible migration will need to implement the functionality that would have been provided by this external dependency.
- **Attribute translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, configuration, and content creation

### Assumptions

1. The external 'nginx' dependency provides standard Nginx installation and configuration capabilities
2. No complex templating or conditional logic exists beyond what's visible in the repository
3. No custom resources or libraries are being used
4. No secrets management or vault integration is required
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
6. The simple HTML content in the index.html file is sufficient for testing purposes

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Default variables from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Tasks from recipes/default.rb
│   │   └── files/
│   │       └── index.html
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Tasks from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── site.yml  # Main playbook
```

## Timeline Estimate

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 2 hours
- Documentation: 2 hours

Total: 1 day (8 hours) for a complete migration
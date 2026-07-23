# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a cache cookbook. The migration scope is relatively small, with two Chef cookbooks to migrate. Based on the complexity and size, this migration can be completed in approximately 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation, service management, and basic content creation. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in the metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management were identified in the repository
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443
  - TLS/SSL certificate management (not present in original code but recommended)
  - Nginx security hardening

### Technical Challenges

- **Attribute to Variable Conversion**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables with appropriate defaults
- **External Dependency**: The external 'nginx' dependency needs to be replaced with an appropriate Ansible Galaxy role or custom implementation
- **Service Management**: Ensure proper service management for both Nginx and Redis services

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The repository is a simple example/test cookbook as indicated in the README.md and not a production-grade implementation
2. The external 'nginx' dependency is not included in the repository and would need to be sourced separately
3. No complex configurations, templates, or custom resources are used beyond what is visible in the repository
4. No secrets management or security-specific configurations are present
5. No custom attributes beyond those in `attributes/default.rb` are used
6. The target environment supports both Ubuntu 18.04+ and CentOS 7.0+ as specified in the metadata files

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/   # Converted from simple-nginx cookbook
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── templates/
│   │       └── index.html.j2
│   └── redis/   # Converted from cache cookbook
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml
└── site.yml     # Main playbook
```
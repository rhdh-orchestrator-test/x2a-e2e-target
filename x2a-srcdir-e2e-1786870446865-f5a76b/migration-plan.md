# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on Nginx installation with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: ./ (root directory)
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
- `README.md`: Documentation file explaining the cookbook's purpose and structure.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible nginx role or direct package installation
- **cache (1.0.0)**: Local dependency that installs Redis, should be migrated to an Ansible role for Redis installation

### Security Considerations

- No explicit security configurations were identified in the examined files
- No credential patterns or secrets management were detected
- Basic service configuration should maintain the same security posture in Ansible

### Technical Challenges

- **Dependency Management**: The cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use a community Nginx role.
- **Configuration Translation**: Attributes in Chef need to be properly mapped to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Main cookbook that depends on cache

### Assumptions

1. The external 'nginx' dependency is used for advanced Nginx configurations not visible in the current repository
2. No complex templating or custom resources are being used
3. No secrets management or vault integration is required
4. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
5. No CI/CD pipeline integration details are provided and will need to be addressed separately
6. No custom handlers or notifications are being used that would require special handling in Ansible

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis/
│       └── tasks/
│           └── main.yml  # Converted from cache cookbook
└── site.yml  # Main playbook
```
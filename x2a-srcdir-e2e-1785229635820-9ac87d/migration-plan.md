# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with Redis caching. The migration scope is relatively small, consisting of one main cookbook with one local dependency. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration parameters for Nginx including port, user, and worker processes. These should be converted to Ansible variables.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management detected in the current codebase
- Basic service security should be implemented in the Ansible roles:
  - Firewall rules for Nginx and Redis
  - Proper file permissions for web content

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on external 'nginx' dependency which is not included in the repository. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Parameters**: Ensure all Nginx configuration parameters from attributes/default.rb are properly mapped to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Convert the Redis cache cookbook to an Ansible role first as it's a dependency
2. **nginx role** (Priority 2): Convert the main Nginx cookbook to an Ansible role

### Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/   # Converted from simple-nginx cookbook
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── templates/
│   │       └── index.html.j2
│   └── redis/   # Converted from cache cookbook
│       └── tasks/
│           └── main.yml
└── site.yml     # Main playbook
```

### Assumptions

1. The cookbook is intended for basic Nginx deployment with Redis caching
2. No complex configuration or customization is required
3. No specific security requirements beyond basic service configuration
4. No specific environment variables or secrets management needed
5. The external 'nginx' dependency is a standard Chef cookbook with no custom modifications
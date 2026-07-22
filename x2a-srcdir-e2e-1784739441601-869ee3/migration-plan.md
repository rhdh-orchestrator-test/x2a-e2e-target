# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook structure for Nginx installation with a local dependency on a cache cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

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

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `ansible.nginx` or create a custom Nginx role
- **cache (1.0.0)**: Convert the local cache cookbook to an Ansible role for Redis installation

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credentials or secrets management detected
- Standard service ports (80 for Nginx, default for Redis) should be reviewed for security best practices
- Vault/secrets management:
  - No credentials detected in either module

### Technical Challenges

- **External Dependency**: The 'nginx' dependency is declared but not included in the repository. The migration will need to determine the exact requirements and functionality needed from this dependency.
- **Configuration Management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, depends on cache

### Assumptions

1. The external 'nginx' dependency is used for advanced configuration not present in the simple cookbook
2. The Redis cache is a required component for the application stack
3. No custom templates or complex configurations are needed beyond what's visible in the code
4. No specific security hardening is required for either Nginx or Redis
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
6. No authentication or TLS/SSL is required for either service
7. The cookbook is intended for a simple web server setup without complex routing or load balancing

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/   # Converted from simple-nginx cookbook
│   └── redis/   # Converted from cache cookbook
└── site.yml     # Main playbook combining both roles
```

## Migration Steps

1. Create Ansible roles structure for both nginx and redis
2. Convert Chef resources to Ansible modules:
   - `package` resources → `ansible.builtin.package` or specific modules like `apt` or `yum`
   - `service` resources → `ansible.builtin.service`
   - `file` resources → `ansible.builtin.file` or `ansible.builtin.copy`
3. Convert Chef attributes to Ansible variables
4. Create a main playbook that applies both roles
5. Test the playbook against supported operating systems
6. Document the new Ansible structure and usage

## Timeline Estimate

- Analysis and planning: 2 hours
- Role creation and resource conversion: 4 hours
- Testing and validation: 4 hours
- Documentation: 2 hours

Total estimated effort: 12 hours (1-2 days)
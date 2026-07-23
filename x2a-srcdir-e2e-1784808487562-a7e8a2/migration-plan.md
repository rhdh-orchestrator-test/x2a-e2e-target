# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with a local cache dependency. The migration scope is relatively small, consisting of one main cookbook and one dependency cookbook. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version not specified)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (1.0.0)**: Create an Ansible role for Redis server installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443
  - TLS/SSL implementation
  - Proper file permissions
- Vault/secrets management:
  - No credentials detected in the current codebase

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that will need to be replaced with an appropriate Ansible role or task
- **Configuration Translation**: Converting Chef attributes to Ansible variables while maintaining the same functionality

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The external 'nginx' dependency is used for advanced configurations not visible in the current codebase
2. No complex Chef resources or custom resources are being used beyond what's visible in the recipes
3. No Berksfile or Policyfile exists for external dependency management
4. No environment-specific configurations exist
5. No data bags or encrypted secrets are being used
6. The Chef cookbook is designed for a simple web server setup without complex requirements

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from simple-nginx/recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # Converted from file resource
│   │   └── defaults/
│   │       └── main.yml  # Converted from attributes/default.rb
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── playbook.yml  # Main playbook applying the roles
```

## Migration Steps

1. Create Ansible directory structure
2. Convert Chef attributes to Ansible variables
3. Convert Redis cache recipe to Ansible role
4. Convert Nginx recipe to Ansible role
5. Create main playbook to apply roles
6. Test deployment in isolated environment
7. Document any configuration differences or improvements
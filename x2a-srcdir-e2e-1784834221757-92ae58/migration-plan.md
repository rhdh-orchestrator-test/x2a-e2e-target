# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: /
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `README.md`: Documentation explaining the cookbook's purpose and structure. Should be updated to reflect Ansible role structure.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy nginx role or direct package installation task
- **cache (1.0.0)**: Migrate the local cache cookbook to an Ansible role for Redis installation

### Security Considerations

- No explicit security configurations or credentials were found in the examined files
- Standard service security practices should be applied in the Ansible roles:
  - Firewall rules for Nginx and Redis
  - Appropriate file permissions for web content
  - Redis access control configuration

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either:
  1. Implement the nginx functionality directly in the role
  2. Use an Ansible Galaxy nginx role as a dependency
  3. Create a separate nginx role in the same project

- **Configuration Management**: Convert Chef attributes to Ansible variables while maintaining the same configuration options

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Depends on cache, moderate complexity

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Port, user, worker_processes variables
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation, service management
│   │   └── templates/
│   │       └── index.html.j2  # Template for index page
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Redis installation, service management
│       └── defaults/
│           └── main.yml  # Redis configuration variables
└── playbook.yml  # Main playbook applying roles
```

### Assumptions

1. The Chef cookbook is designed for Ubuntu 18.04+ or CentOS 7.0+ environments
2. The external 'nginx' dependency is a standard Chef cookbook that handles basic Nginx installation
3. No custom configurations beyond what's visible in the examined files
4. No complex integrations or orchestration between Nginx and Redis beyond basic installation
5. No secrets management or security-specific configurations are present
6. No custom templates or additional files beyond what was discovered in the repository
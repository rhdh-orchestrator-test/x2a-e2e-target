# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook "simple-nginx" and a local dependency cookbook "cache". The migration scope is relatively small, with only two cookbooks that have straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation and configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for installing nginx, ensuring the service is running, and creating a simple index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in the metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible nginx role or direct package installation tasks
- **redis-server (unspecified version)**: Replace with Ansible redis role or direct package installation tasks

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No vault/secrets management was detected
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for nginx configuration
  - Redis security best practices (password protection, network binding)

### Technical Challenges

- **External nginx dependency**: The cookbook depends on an external 'nginx' cookbook that is not included in the repository. The migration will need to either:
  1. Incorporate the functionality directly in the Ansible role
  2. Find an equivalent Ansible Galaxy role for nginx
  3. Determine what specific functionality from the external cookbook was being used

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/   # Converted from simple-nginx cookbook
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── templates/
│   │   │   └── index.html.j2
│   │   └── defaults/
│   │       └── main.yml
│   └── redis/   # Converted from cache cookbook
│       ├── tasks/
│       │   └── main.yml
│       └── defaults/
│           └── main.yml
└── site.yml     # Main playbook
```

### Assumptions

1. The external 'nginx' cookbook dependency is used only for basic nginx installation and not for complex configurations
2. No custom templates or additional files are used beyond what was discovered in the repository
3. No specific nginx configuration beyond the default is required
4. Redis is used with default configuration settings
5. No specific security hardening is required beyond standard practices
6. No complex integration between nginx and redis is implemented
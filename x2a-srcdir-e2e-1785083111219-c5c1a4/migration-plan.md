# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for a basic Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs and configures Nginx with a basic welcome page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible roles.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index.html file.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (1.0.0)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Basic file permissions are set for the index.html file (mode '0644')
- No credentials or sensitive data detected in the repository
- Vault/secrets management:
  - No encrypted data bags or Chef Vault usage detected
  - No hardcoded credentials found
  - No SSL/TLS certificate references
  - No environment variable secrets

### Technical Challenges

- **Dependency Management**: The cookbook relies on an external 'nginx' dependency that is declared but not included. The migration will need to either incorporate this functionality directly or use an equivalent Ansible Galaxy role.
- **Configuration Translation**: Converting Chef attributes to Ansible variables while maintaining the same behavior.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management, low complexity
2. **nginx role** (Priority 2): Main web server configuration, depends on cache role

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # Template for the index page
│   │   └── defaults/
│   │       └── main.yml  # Default variables
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── playbook.yml  # Main playbook that applies roles
```

### Assumptions

1. The cookbook is intended for a simple web server setup with Redis caching
2. No complex configuration or customization is required beyond what's explicitly defined
3. No special handling is needed for different OS distributions beyond what's supported
4. The external 'nginx' dependency provides standard Nginx functionality that can be replaced with a standard Ansible role
5. No specific performance tuning or advanced features are required
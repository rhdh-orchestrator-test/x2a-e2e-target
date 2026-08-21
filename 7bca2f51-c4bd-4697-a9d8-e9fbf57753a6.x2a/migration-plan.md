# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for a basic Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with one local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple Redis cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified, assume standard VM environment
- **Cloud Platform**: Not specified, appears to be cloud-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` module or community.general collection
- **cache (local)**: Convert to Ansible role for Redis installation and configuration
- **redis-server**: Use Ansible's package module to install Redis

### Security Considerations

- No explicit security configurations were found in the codebase
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443
  - TLS/SSL configuration for Nginx
  - Redis security (password protection, network binding)

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on external 'nginx' dependency which is declared but not included. The Ansible equivalent will need to either incorporate the necessary Nginx configuration directly or use an Ansible Galaxy role.
- **Configuration Management**: Converting Chef attributes to Ansible variables while maintaining the same functionality.

### Migration Order

1. Create base Ansible directory structure with roles and playbooks
2. Migrate cache cookbook to Ansible role (simple Redis installation)
3. Migrate simple-nginx cookbook to Ansible role (Nginx configuration)
4. Create main playbook that includes both roles
5. Test deployment on supported platforms (Ubuntu 18.04+ and CentOS 7+)

### Assumptions

- The Chef cookbook is designed for a simple web server setup with Redis caching
- No complex configuration or customization is required beyond basic installation
- No secrets management or certificates are currently in use
- The cookbook is intended for testing purposes as indicated in the README
- The external 'nginx' dependency is not critical and can be replaced with direct Ansible tasks

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
│   │   ├── templates/
│   │   │   └── index.html.j2  # Template for index page
│   │   └── defaults/
│   │       └── main.yml  # Default variables
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Default variables
└── site.yml  # Main playbook that includes both roles
```

## Timeline Estimate

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing and validation: 4 hours
- Documentation: 2 hours

Total estimated effort: 12 hours (1-2 days)
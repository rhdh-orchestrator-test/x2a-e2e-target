# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on deploying Nginx with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should account for these dependencies in Ansible roles.
- `attributes/default.rb`: Contains configuration parameters for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index.html file.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in the metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Create an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were found in the cookbooks
- No secrets management or credential patterns were detected
- Basic service security should be implemented in the Ansible roles:
  - Firewall rules for Nginx and Redis
  - Proper file permissions for web content

### Technical Challenges

- **Dependency Management**: The original cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Galaxy role.
- **Configuration Parameters**: Ensure all attributes from `attributes/default.rb` are properly mapped to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Create an Ansible role for Redis installation and configuration
2. **nginx role** (Priority 2): Create an Ansible role for Nginx with the appropriate configuration

### Assumptions

1. The external 'nginx' dependency was used for advanced configuration not present in the simple-nginx cookbook itself
2. No complex templating or conditional logic exists in the current cookbooks
3. No custom resources or libraries are being used
4. No secrets management is required
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7+
6. No specific performance tuning or advanced configurations are needed beyond what's explicitly defined in the cookbooks

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
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
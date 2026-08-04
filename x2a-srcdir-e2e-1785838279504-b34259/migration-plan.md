# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible roles.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration
- **Chef 16.0+**: No direct replacement needed, but ensure Ansible version is compatible with target systems

### Security Considerations

- No explicit security configurations or secrets management were identified in the codebase
- Standard service security practices should be implemented in the Ansible roles:
  - Nginx configuration should include secure defaults
  - Redis should be configured with authentication if exposed beyond localhost

### Technical Challenges

- **Simple Conversion**: The cookbook is straightforward with minimal complexity, making migration relatively simple
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults
- **External Dependencies**: The external 'nginx' dependency needs to be addressed, either by creating a custom role or using an existing Ansible Galaxy role

### Migration Order

1. **cache role** (Priority 1): Convert the Redis cache cookbook to an Ansible role first as it's a dependency
2. **nginx role** (Priority 2): Convert the main Nginx cookbook to an Ansible role

### Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   └── hosts
├── group_vars/
│   └── all.yml  # Former Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Former Chef attributes
│   │   ├── tasks/
│   │   │   └── main.yml  # Former Chef recipes
│   │   └── templates/
│   │       └── index.html.j2  # Former static content
│   └── redis_cache/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml  # Former cache cookbook recipes
└── site.yml  # Main playbook
```

### Assumptions

- The cookbook is intended for a simple Nginx deployment with Redis caching
- No complex configurations or customizations are required
- No secrets management or security hardening is implemented in the current code
- The external 'nginx' dependency is used for additional Nginx configurations not present in the main cookbook
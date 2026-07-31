# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on Nginx installation with a local cache dependency. The migration scope is relatively small, consisting of two Chef cookbooks with minimal complexity. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external)
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis cache server installation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation task
- **cache (local)**: Migrate to Ansible redis installation tasks or role

### Security Considerations

- No explicit security configurations or secrets management detected
- Standard service configurations should maintain default security settings
- No credentials detected in the codebase

### Technical Challenges

- **Simple Configuration**: The cookbooks are straightforward with minimal complexity, presenting few migration challenges
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables
- **Service Management**: Ensure proper service management in Ansible equivalent

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Migration Structure

Recommended Ansible structure:

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # For nginx and redis variables
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation tasks
│   │   └── templates/
│   │       └── index.html.j2  # Template for index page
│   └── redis/
│       └── tasks/
│           └── main.yml  # Redis installation tasks
└── site.yml  # Main playbook
```

### Ansible Variable Mapping

Chef attributes to Ansible variables:
- `default['nginx']['port']` → `nginx_port`
- `default['nginx']['user']` → `nginx_user`
- `default['nginx']['worker_processes']` → `nginx_worker_processes`

### Assumptions

- The cookbooks are intended for testing purposes as indicated in the README
- The nginx configuration is minimal with no complex customizations
- Redis is used as a simple cache with default configuration
- No specific environment variables or secrets management is required
- No complex deployment workflows or orchestration is needed
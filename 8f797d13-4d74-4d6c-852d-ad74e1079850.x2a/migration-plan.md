# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan covers the conversion of a Chef cookbook repository to Ansible. The repository contains a main cookbook called `simple-nginx` and a local dependency cookbook called `cache`. The main cookbook installs and configures Nginx web server, while the cache cookbook installs and configures Redis as a caching solution.

The migration is relatively straightforward with low complexity due to the small number of cookbooks and simple configurations. Estimated timeline: 1-2 days for a single developer to complete the migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata file defining dependencies and supported platforms
  - Migration consideration: Convert dependencies to Ansible Galaxy requirements
  
- `attributes/default.rb`: Default attributes for Nginx configuration
  - Migration consideration: Convert to Ansible variables in defaults/main.yml
  
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
  - Migration consideration: Convert to Ansible tasks in tasks/main.yml
  
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata
  - Migration consideration: Convert to separate Ansible role metadata
  
- `cookbooks/cache/recipes/default.rb`: Cache cookbook recipe for Redis installation
  - Migration consideration: Convert to Ansible tasks in a separate role

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx collection or create custom Nginx role
- **cache (1.0.0)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443 (Nginx) and 6379 (Redis)
  - TLS/SSL configuration for Nginx
  - Redis password protection
- Vault/secrets management:
  - No credentials or secrets detected in the repository

### Technical Challenges

- **External dependency handling**: The `nginx` dependency is declared but not included in the repository. The migration will need to either:
  1. Use the Ansible community.nginx collection
  2. Create a custom Nginx role based on the Chef cookbook's functionality
  
- **Configuration management**: Ensure Nginx configuration parameters from attributes are properly mapped to Ansible variables

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content deployment

### Assumptions

1. The repository is using a metadata-only dependency strategy as mentioned in the README
2. The external `nginx` dependency is not critical for understanding the cookbook's functionality
3. No complex configurations or templates are being used beyond what's visible in the repository
4. No secrets management or security configurations are present
5. The cookbook is designed for testing purposes rather than production use

## Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Variables from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Logic from recipes/default.rb
│   │   └── meta/
│   │       └── main.yml  # Dependencies information
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # Logic from cookbooks/cache/recipes/default.rb
│       └── meta/
│           └── main.yml  # Dependencies information
├── playbook.yml  # Main playbook that includes both roles
└── requirements.yml  # External dependencies (community.nginx)
```

## Implementation Notes

1. **Nginx Role**:
   - Convert package installation to `ansible.builtin.package` module
   - Convert service management to `ansible.builtin.service` module
   - Convert file creation to `ansible.builtin.copy` or `ansible.builtin.template` module
   - Map attributes to variables in defaults/main.yml

2. **Cache Role**:
   - Convert Redis package installation to `ansible.builtin.package` module
   - Convert Redis service management to `ansible.builtin.service` module

3. **Variables**:
   - Map `node['nginx']['port']` to `nginx_port`
   - Map `node['nginx']['user']` to `nginx_user`
   - Map `node['nginx']['worker_processes']` to `nginx_worker_processes`

4. **Testing**:
   - Implement molecule tests for both roles
   - Test on both Ubuntu 18.04+ and CentOS 7.0+ as specified in the original metadata
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for this migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: ./ (root directory with recipes/default.rb)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata file defining dependencies and supported platforms
  - Migration considerations: Dependencies need to be mapped to Ansible roles or collections
  
- `attributes/default.rb`: Default attributes for nginx configuration
  - Migration considerations: Convert to Ansible variables in defaults/main.yml

- `cookbooks/cache/metadata.rb`: Cache cookbook metadata file
  - Migration considerations: Convert to Ansible role metadata

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy community.general.nginx role or direct package installation
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Standard service configurations without specific security hardening

### Technical Challenges

- **External dependency handling**: The nginx dependency is declared but not included in the repository. The Ansible migration will need to either incorporate nginx configuration directly or establish a dependency on an Ansible Galaxy role.
- **Attribute to variable mapping**: Convert Chef attributes to Ansible variables with appropriate defaults and overrides.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Depends on cache, slightly more configuration

### Assumptions

1. The external nginx dependency is a standard Chef cookbook without custom modifications
2. No complex Chef-specific features (like search, data bags, environments) are being used
3. No custom resources or libraries are present that would require special handling
4. The cookbooks are used in a straightforward manner without complex node attribute overrides
5. No integration with external services or APIs beyond basic package installation
6. No authentication or authorization mechanisms are implemented
7. No complex templating or file generation beyond the simple index.html file

## Ansible Migration Details

### Role Structure

The migration will create two Ansible roles:

1. **nginx_role**:
   - tasks/main.yml: Install nginx package, enable and start service, create index.html
   - defaults/main.yml: Variables for nginx port, user, worker_processes
   - meta/main.yml: Role metadata including dependencies

2. **redis_cache_role**:
   - tasks/main.yml: Install redis-server package, enable and start service
   - meta/main.yml: Role metadata

### Playbook Structure

A main playbook will be created to orchestrate the roles:

```yaml
---
- name: Deploy Nginx with Redis Cache
  hosts: web_servers
  become: true
  roles:
    - redis_cache_role
    - nginx_role
```

### Variable Mapping

Chef attributes will be mapped to Ansible variables:

```yaml
# defaults/main.yml for nginx_role
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Testing Strategy

1. Create test inventory with Ubuntu and CentOS targets
2. Develop and test each role independently
3. Test the integrated playbook
4. Verify functionality matches original Chef implementation
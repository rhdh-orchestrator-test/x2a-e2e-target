# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to convert. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Convert dependencies to Ansible roles or collections.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Migration consideration: Convert to Ansible role metadata.
- `attributes/default.rb`: Contains configuration attributes for nginx. Migration consideration: Convert to Ansible variables.

### Target Details

Based on the source repository analysis:

- **Operating System**: The cookbooks support Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the metadata.rb files.
- **Virtual Machine Technology**: Not specified in the repository.
- **Cloud Platform**: Not specified in the repository.

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible nginx role or use the `ansible.builtin.package` module to install nginx
- **cache (1.0.0)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks.
- No credentials or secrets management was found in the examined files.
- Basic file permissions are set for the index.html file (mode '0644').

### Technical Challenges

- **External Dependencies**: The cookbook depends on an external 'nginx' cookbook which is declared but not included in the repository. The Ansible migration will need to implement the functionality directly or use a community role.
- **Service Configuration**: Ensure proper service management for nginx and redis-server in the Ansible roles.

### Migration Order

1. **cache cookbook** (Priority 1): Convert to Ansible role first as it's a dependency for the main cookbook.
2. **simple-nginx cookbook** (Priority 2): Convert to Ansible role after the cache role is completed.

### Assumptions

1. The external nginx cookbook dependency is used only for its package installation and service management, which can be directly implemented in Ansible.
2. No complex configurations or templates are used beyond what's visible in the examined files.
3. No custom resources or libraries are used in the cookbooks.
4. The cookbooks are intended for basic installation and configuration of nginx and redis services without advanced customization.
5. No secrets management or security-specific configurations are required.
6. The target environment will continue to be Ubuntu (>= 18.04) or CentOS (>= 7.0).
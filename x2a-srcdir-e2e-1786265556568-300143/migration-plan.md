# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook "simple-nginx" and a local dependency cookbook "cache". The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, and simple index page creation

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and platform support. Will be replaced by Ansible metadata in roles or collections.
- `attributes/default.rb`: Contains default attributes for the nginx configuration. Will be migrated to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing and configuring nginx. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will be replaced by Ansible metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or direct package installation tasks
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration
- **redis-server**: Direct package installation via Ansible's package module

### Security Considerations

- No explicit security configurations identified in the current cookbooks
- Basic service management for nginx and redis-server
- No credentials or secrets management detected

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through role requirements or collections.
- **Configuration Management**: Nginx configuration attributes will need to be converted to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
   - Low complexity, no dependencies
   - Create an Ansible role for Redis installation

2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration
   - Depends on the cache role
   - Create an Ansible role for Nginx with appropriate variables

### Assumptions

1. The nginx cookbook dependency is an external dependency not included in the repository
2. No complex configuration templates are used for either nginx or redis
3. No custom resources or libraries are used in the cookbooks
4. No secrets management or vault integration is required
5. The cookbooks are designed for testing purposes and may not represent production-ready configurations
6. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
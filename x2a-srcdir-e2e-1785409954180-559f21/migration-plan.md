# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `README.md`: Documentation file explaining the cookbook's purpose and structure.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (1.0.0)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Firewall rules for Nginx (port 80) and Redis
  - Redis binding and authentication configuration
  - Nginx security headers and configurations

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on external 'nginx' dependency which is declared but not included. The Ansible migration will need to implement this functionality directly or use a community role.
- **Configuration Management**: Ensure that all Chef attributes are properly mapped to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The current Chef implementation is minimal and likely for demonstration purposes only
2. No complex configurations or templates are being used
3. No secrets management or vault integration is present
4. The external 'nginx' dependency may provide functionality not visible in the current codebase
5. No custom resources or libraries are being used
6. No complex conditionals or platform-specific code is present

## Migration Steps

1. **Create Ansible Directory Structure**:
   ```
   ansible/
   ├── inventory/
   │   └── hosts
   ├── group_vars/
   │   └── all.yml
   ├── roles/
   │   ├── nginx/
   │   └── redis/
   └── site.yml
   ```

2. **Convert Chef Attributes to Ansible Variables**:
   - Map `node['nginx']['port']` to `nginx_port`
   - Map `node['nginx']['user']` to `nginx_user`
   - Map `node['nginx']['worker_processes']` to `nginx_worker_processes`

3. **Create Redis Role** (from cache cookbook):
   - Tasks for package installation
   - Service management
   - Configuration templates if needed

4. **Create Nginx Role** (from simple-nginx cookbook):
   - Tasks for package installation
   - Service management
   - Static content creation
   - Configuration templates

5. **Create Main Playbook** (site.yml):
   - Include both roles with appropriate variables

6. **Testing**:
   - Validate against the same OS versions supported by the original cookbook
   - Verify functionality of both Nginx and Redis services

## Timeline Estimate

- **Analysis and Planning**: 2 hours (completed)
- **Role Development**: 4-6 hours
- **Testing and Validation**: 2-4 hours
- **Documentation**: 1-2 hours
- **Total**: 9-14 hours (1-2 days)
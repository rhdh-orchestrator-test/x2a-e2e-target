# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` that installs and configures Nginx with basic settings. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with only two cookbooks to migrate: the main `simple-nginx` cookbook and its local dependency `cache` cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx web server, configures basic settings, and creates a default index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
  - Migration consideration: Dependencies need to be mapped to Ansible roles or collections
  
- `attributes/default.rb`: Contains default attributes for Nginx configuration
  - Migration consideration: Convert to Ansible variables in defaults/main.yml

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy community.nginx role or create a custom Nginx role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be implemented in the Ansible roles:
  - Firewall rules for Nginx (port 80) and Redis
  - Redis password protection (not implemented in the original cookbook)

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or as collections.
- **Configuration Management**: Attributes in Chef need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and configuration
2. **nginx role** (Priority 2): Nginx installation with configuration from attributes

### Assumptions

1. The cookbook is used in a simple environment without complex integrations
2. No custom templates or complex configurations are used beyond what's visible in the repository
3. No secrets management or security hardening is implemented in the current cookbook
4. The external nginx dependency provides standard Nginx functionality that can be replaced with community.nginx or a custom role
5. No CI/CD pipeline integration is required for the migration
6. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+

## Migration Steps

1. **Create Ansible Directory Structure**:
   ```
   ansible-simple-nginx/
   ├── inventories/
   │   └── production/
   │       ├── hosts
   │       └── group_vars/
   │           └── all.yml
   ├── roles/
   │   ├── nginx/
   │   │   ├── defaults/
   │   │   │   └── main.yml  # Convert from attributes/default.rb
   │   │   ├── tasks/
   │   │   │   └── main.yml  # Convert from recipes/default.rb
   │   │   └── templates/
   │   │       └── index.html.j2
   │   └── redis/
   │       ├── defaults/
   │       │   └── main.yml
   │       └── tasks/
   │           └── main.yml  # Convert from cookbooks/cache/recipes/default.rb
   ├── site.yml
   └── requirements.yml  # For external dependencies
   ```

2. **Convert Chef Attributes to Ansible Variables**:
   - Move Nginx configuration from attributes/default.rb to roles/nginx/defaults/main.yml
   - Format as YAML instead of Ruby

3. **Convert Chef Resources to Ansible Tasks**:
   - Convert package resources to Ansible package modules
   - Convert service resources to Ansible service modules
   - Convert file resources to Ansible template or copy modules

4. **Create Playbook**:
   - Create site.yml that includes both roles
   - Ensure proper role ordering

5. **Testing**:
   - Test the Ansible playbook against the same target platforms (Ubuntu 18.04+, CentOS 7.0+)
   - Verify Nginx and Redis are installed and running correctly

6. **Documentation**:
   - Create README.md with usage instructions
   - Document variables and their default values
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on maintaining the dependency relationship and basic web server functionality. Estimated timeline: 1-2 weeks for a small team, given the straightforward nature of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, custom HTML content, attribute-driven configuration

- **cache**:
    - Description: Redis server installation and configuration for caching services
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management, basic cache functionality

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management

### Security Considerations
- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 and root ownership - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd service configuration in target environment
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges
- **External dependency resolution**: The root cookbook depends on an external 'nginx' cookbook that is not present in the repository - this dependency will need to be resolved or replaced with direct Ansible nginx configuration
- **Metadata-only strategy**: The current setup uses Chef's metadata.rb for dependency declaration without Berksfile or Policyfile - Ansible equivalent will use ansible-galaxy requirements.yml or direct role dependencies
- **Attribute translation**: Chef attributes in `attributes/default.rb` need conversion to Ansible variables in defaults/main.yml or group_vars

### Migration Order
1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and custom content creation)

### Assumptions
- The external 'nginx' cookbook dependency mentioned in metadata.rb is not critical for basic functionality, as the recipe directly uses the 'nginx' package
- Target systems will have package managers (apt/yum) available for nginx and redis-server packages
- The current Chef cookbook supports both Ubuntu and CentOS, so Ansible playbooks should maintain this cross-platform compatibility
- No complex nginx configuration is required beyond basic installation and service management
- Redis configuration can remain at default settings as no custom configuration files are specified in the cache cookbook
- The metadata-only dependency strategy is for testing purposes and can be simplified in the Ansible migration
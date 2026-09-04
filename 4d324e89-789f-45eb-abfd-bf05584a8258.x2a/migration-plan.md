# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration scope is relatively straightforward, involving two cookbooks with basic web server and caching functionality. Estimated timeline: 1-2 weeks for a small team, with low complexity due to minimal dependencies and straightforward resource management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server cookbook with basic package installation, service management, and static content deployment
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Nginx package installation, service enablement and startup, custom index.html creation, configurable port and worker processes

- **cache**:
    - Description: Redis cache server cookbook providing basic caching functionality as a local dependency
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis-server package installation, service management, basic cache infrastructure

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external) cookbooks, platform support for Ubuntu 18.04+ and CentOS 7+
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform compatibility definitions
- `attributes/default.rb`: Nginx configuration attributes including port (80), user (www-data), and worker processes (auto)
- `recipes/default.rb`: Main nginx installation and configuration recipe
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management recipe

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules for nginx installation and management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules for Redis cache functionality
- **cache (local cookbook)**: Convert to Ansible role or integrate directly into playbook structure

### Security Considerations
- **File permissions**: Static HTML file creation uses explicit mode '0644', owner 'root', group 'root' - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain secure service states
- **Vault/secrets management**: No encrypted data bags, Chef Vault usage, or hardcoded credentials detected in any module. No SSL/TLS certificate references found. No environment variable secrets identified. Credential count: 0 across all modules.

### Technical Challenges
- **External nginx dependency**: The metadata declares dependency on external 'nginx' cookbook that is not present in repository - need to identify what additional nginx configuration this provides
- **Platform compatibility**: Cookbook supports both Ubuntu and CentOS with different package names (redis-server vs redis) - Ansible playbooks need conditional package installation logic
- **Service naming variations**: Redis service name may differ between platforms - require platform-specific service management

### Migration Order
1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions
- The external 'nginx' cookbook dependency provides standard nginx configuration that can be replaced with basic Ansible nginx setup
- Redis package naming follows standard conventions (redis-server on Ubuntu, redis on CentOS)
- No custom nginx configuration files are required beyond the basic installation
- The static HTML content creation is sufficient and no dynamic templating is needed
- Chef version requirement '>= 16.0' indicates modern Chef practices that should translate well to current Ansible versions
- No encrypted data bags or secrets management is required based on the simple nature of the cookbooks
- The cookbook is designed for testing purposes and may not represent production-level complexity
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ as explicitly defined in metadata
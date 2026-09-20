# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles. This is a low-complexity migration with minimal dependencies and straightforward service management patterns. Estimated timeline: 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Nginx web server installation and configuration with basic service management and custom index page deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on cache and nginx cookbooks
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role with redis installation and configuration

### Security Considerations
- File permissions: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible
- Service security: No specific security configurations identified in the current implementation
- Vault/secrets management: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges
- External nginx dependency: The metadata declares a dependency on an external 'nginx' cookbook that is not present in the repository - this suggests the cookbook relies on external cookbook sources that need to be identified and replaced with appropriate Ansible modules
- Attribute translation: Chef attributes need to be converted to Ansible variables with appropriate defaults
- Service dependency ordering: Ensure proper task ordering between package installation and service management

### Migration Order
1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx cookbook dependency)

### Assumptions
- The external 'nginx' cookbook dependency is used for advanced nginx configuration not visible in the current simple recipe
- Target systems have package managers compatible with the 'package' resource (apt for Ubuntu, yum/dnf for CentOS)
- Redis package name 'redis-server' is consistent across target platforms (may need platform-specific handling)
- No custom nginx configuration files are required beyond the basic service setup shown
- The cookbook is intended for development/testing environments given its simplicity and lack of security hardening
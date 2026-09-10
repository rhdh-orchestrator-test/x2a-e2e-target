# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles. This is a low-complexity migration with minimal dependencies and straightforward service management patterns. Estimated timeline: 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining simple-nginx cookbook with dependencies on cache and nginx
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role dependency in requirements.yml

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644, owner root:root - maintain in Ansible file module
- **Service management**: Both nginx and redis services use standard systemd management - straightforward Ansible conversion
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External nginx dependency**: The metadata declares dependency on external 'nginx' cookbook not present in repository - will need to implement nginx configuration directly in Ansible or source appropriate role
- **Metadata-only strategy**: Repository designed for testing dependency resolution without actual cookbook fetching - migration must account for missing external dependencies
- **Platform compatibility**: Cookbooks support both Ubuntu and CentOS - Ansible playbooks should maintain cross-platform compatibility using package module and conditional tasks

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- External nginx cookbook functionality will need to be implemented directly in Ansible since the cookbook is not present in the repository
- Target systems will have package managers (apt/yum) available for nginx and redis installation
- Default nginx configuration will be sufficient, as no custom nginx.conf templates are present
- Redis will use default configuration since no custom redis.conf management is implemented
- The metadata-only testing strategy indicates this is a development/testing environment rather than production
- Service management assumes systemd-based systems given the Chef service resource usage
- No custom firewall rules or security hardening beyond basic file permissions are required
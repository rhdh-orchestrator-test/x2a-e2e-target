# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles. This is a low-complexity migration with minimal dependencies and straightforward service management patterns. Estimated timeline: 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Nginx web server installation and configuration with basic service management and custom index page
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support declarations

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to separate Ansible role for Redis installation

### Security Considerations
- File permissions: Static HTML file created with explicit mode 0644, owner root:root - maintain in Ansible with ansible.builtin.file module
- Service management: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- Vault/secrets management: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges
- **Cookbook Dependencies**: The main cookbook depends on both a local 'cache' cookbook and external 'nginx' cookbook - need to restructure as separate Ansible roles with proper role dependencies
- **Attribute System**: Chef attributes need conversion to Ansible variables with proper precedence and default values
- **Platform Support**: Metadata declares support for both Ubuntu and CentOS - ensure Ansible playbooks handle package manager differences (apt vs yum)

### Migration Order
1. **cache** cookbook (low risk, no dependencies, simple Redis installation)
2. **simple-nginx** cookbook (depends on cache, moderate complexity with file management)

### Assumptions
- The external 'nginx' dependency mentioned in metadata.rb is not present in the repository and may need to be sourced separately or replaced with native Ansible nginx installation
- Default nginx configuration is sufficient as no custom nginx.conf templates are present
- Redis configuration uses default settings as no custom configuration files are specified
- Target systems have internet access for package installation
- The cookbook is intended for development/testing environments given its simplicity
- No SSL/TLS configuration is required based on the basic setup observed
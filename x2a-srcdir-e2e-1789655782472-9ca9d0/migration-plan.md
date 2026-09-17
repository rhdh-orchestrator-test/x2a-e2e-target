# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small but demonstrates key Chef patterns including cookbook dependencies, attribute management, and service configuration. Estimated timeline: 1-2 weeks for a small team, with low complexity due to the straightforward nature of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Nginx package installation, service management, basic HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management and startup configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode '0644' and root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **Package installation**: No version pinning observed - consider implementing version constraints in Ansible for reproducible deployments
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external 'nginx' dependency that may not be resolvable without Berksfile or Policyfile - need to identify the actual nginx cookbook source or replace with community Ansible roles
- **Attribute inheritance**: Chef attributes system needs to be replaced with Ansible variables and defaults structure
- **Service ordering**: Ensure proper dependency ordering between nginx and cache services in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in metadata

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity, depends on cache module, external nginx dependency to resolve)

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb will need to be replaced with a community Ansible role or custom implementation since no Berksfile/Policyfile exists to resolve it
- The cookbook is designed for testing metadata-only dependency strategies, so production hardening may be minimal
- Default nginx configuration is acceptable since no custom templates or advanced configuration files were found
- Redis configuration uses default settings since no custom configuration templates were identified
- The target environment has internet access for package installation via apt/yum
- No custom SSL/TLS configuration is required based on the simple HTML content and default port 80 usage
- The migration will maintain the same service startup behavior (enable and start both nginx and redis)
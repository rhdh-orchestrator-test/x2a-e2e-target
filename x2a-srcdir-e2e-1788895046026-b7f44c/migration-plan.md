# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook environment demonstrating a metadata-only dependency strategy. The migration scope is relatively straightforward with two cookbooks providing basic web server and caching functionality. Estimated timeline: 1-2 weeks for a small team, with low complexity due to minimal dependencies and straightforward service configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced configuration

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode '0644' and root ownership - ensure Ansible file module maintains proper permissions
- **Service security**: Both nginx and redis services run with default configurations - review security hardening requirements during migration
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **Metadata-only dependency strategy**: The root cookbook declares an external 'nginx' dependency that isn't locally available, requiring resolution of how this external dependency will be handled in Ansible (likely through galaxy roles or custom playbooks)
- **Attribute inheritance**: Chef attributes system needs to be replaced with Ansible variables and defaults, maintaining the same configurability
- **Service management**: Both cookbooks rely on Chef's service resource - ensure proper systemd/init system handling in Ansible equivalents

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external 'nginx' dependency mentioned in metadata.rb is intended to be resolved through an external cookbook repository or will be replaced with direct package management in Ansible
- The target environment has package managers available (apt for Ubuntu, yum/dnf for CentOS) as implied by the Chef package resources
- Default service management (systemd) is available on target systems for nginx and redis services
- The simple HTML content deployment pattern suggests this is a basic web server setup rather than a complex application deployment
- No complex Chef-specific features (encrypted data bags, search, environments) are in use based on the straightforward recipe structure
- Platform support requirements (Ubuntu 18.04+, CentOS 7+) will be maintained in the Ansible implementation
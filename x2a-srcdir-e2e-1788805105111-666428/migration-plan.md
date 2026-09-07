# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

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
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency and platform support declarations
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support for Ubuntu 18.04+ and CentOS 7+
- `attributes/default.rb`: Nginx configuration attributes including port (80), user (www-data), and worker processes (auto)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local)**: Internal dependency that will be converted to an Ansible role and included via dependencies in meta/main.yml

### Security Considerations

- **File permissions**: The cookbook creates /var/www/html/index.html with explicit mode 0644, owner root, group root - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd service configuration in Ansible
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Web server exposure**: Nginx is configured to listen on port 80 - consider SSL/TLS configuration for production deployments

### Technical Challenges

- **External dependency resolution**: The nginx dependency is declared in metadata.rb but no Berksfile or Policyfile exists, suggesting this cookbook relies on external dependency management - Ansible Galaxy or collections will need to provide nginx functionality
- **Metadata-only strategy**: The repository is designed for testing metadata-only dependencies, which may not reflect real-world cookbook complexity - migration testing should validate that all implied functionality works correctly
- **Platform compatibility**: Cookbooks support both Ubuntu and CentOS - Ansible playbooks will need conditional logic for package manager differences (apt vs yum/dnf)

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external nginx dependency will be satisfied by community Ansible collections or roles rather than requiring custom implementation
- The current configuration is intended for development/testing rather than production (no SSL, basic configuration)
- Platform-specific package names (redis-server) may need adjustment for different Linux distributions
- The metadata-only dependency strategy suggests this is a test repository rather than production infrastructure
- No complex Chef-specific features (encrypted data bags, environments, roles) are in use that would complicate migration
- Service management assumes systemd is available on target platforms
- File ownership and permissions requirements are standard and don't require special handling beyond Ansible's file module capabilities
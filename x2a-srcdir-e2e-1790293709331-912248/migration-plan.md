# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching service provisioning. The scope is relatively small but demonstrates key Chef-to-Ansible migration patterns including package management, service control, and file deployment.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Convert to Ansible role with redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File Permissions**: Static HTML file created with explicit mode (0644), owner (root), and group (root) - maintain in Ansible file module
- **Service Security**: No specific security hardening identified in current configuration
- **Vault/secrets management**: No encrypted data bags, vault usage, or credential patterns identified in the reviewed files
- **Network Security**: Default nginx configuration uses port 80 (HTTP) - consider HTTPS upgrade during migration

### Technical Challenges

- **External Dependencies**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible Galaxy role or create custom nginx role
- **Attribute Translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with proper defaults
- **Service Management**: Chef service resource patterns need translation to Ansible service module with equivalent actions
- **Platform Support**: Cookbook supports both Ubuntu and CentOS - Ansible playbooks must handle package manager differences (apt vs yum)

### Migration Order

1. **cache** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx** (moderate complexity, depends on cache role, requires nginx configuration)

### Assumptions

- The external 'nginx' dependency will be replaced with a community Ansible role or custom implementation
- Target systems will have internet access for package installation
- The metadata-only dependency strategy testing purpose suggests this is a development/testing environment rather than production
- No complex nginx configuration is required beyond basic service setup and static content
- Redis configuration can remain at default settings as no custom configuration is present in the cache cookbook
- The migration will maintain the same platform support (Ubuntu 18.04+, CentOS 7+) unless otherwise specified
- No SSL/TLS configuration is required initially, though this should be considered for production deployments
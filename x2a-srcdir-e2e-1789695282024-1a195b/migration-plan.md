# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward web server and caching setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML content deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified in source configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.redis module for advanced configuration
- **cache (local)**: Internal dependency that will be converted to an Ansible role

### Security Considerations

- **File permissions**: Static HTML file creation with explicit mode (0644), owner (root), and group (root) settings need equivalent Ansible file module configuration
- **Service management**: Both nginx and redis services are enabled and started, requiring proper Ansible service state management
- **Package installation**: No version pinning observed, consider implementing version constraints in Ansible for production stability
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual resolution of the appropriate Ansible collection or role
- **Attribute system migration**: Chef attributes system (default['nginx']['port']) needs conversion to Ansible variables with proper precedence handling
- **Cross-cookbook dependencies**: The simple-nginx cookbook depends on the cache cookbook, requiring coordination of Ansible role dependencies
- **Platform support**: Cookbook supports both Ubuntu and CentOS, requiring Ansible playbook conditional logic for package manager differences

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis setup)
2. **simple-nginx** (moderate complexity, depends on cache role and external nginx dependency)

### Assumptions

- The external nginx dependency mentioned in metadata.rb refers to a standard nginx cookbook from Chef Supermarket, not a custom implementation
- The target environment will maintain the same OS support matrix (Ubuntu 18.04+ and CentOS 7.0+)
- No additional configuration files, templates, or complex nginx configurations exist beyond the basic setup shown
- The metadata-only dependency strategy indicates this is a test/example repository rather than a production system
- No encrypted data bags, secrets, or sensitive configuration management is required based on the simple nature of the cookbooks
- The Redis installation uses default configuration without custom redis.conf templates or advanced clustering setup
- No load balancing, SSL/TLS termination, or advanced nginx features are required beyond basic web server functionality
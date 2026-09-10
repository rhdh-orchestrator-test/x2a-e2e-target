# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration scope is relatively straightforward with two cookbooks providing basic web server and caching functionality. Estimated timeline: 1-2 weeks for a small team, with low complexity due to minimal dependencies and straightforward service configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration and custom index page
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx role from Ansible Galaxy
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **Chef 16.0+**: Remove Chef-specific dependency management and replace with Ansible native modules

### Security Considerations

- **File permissions**: Static file creation uses explicit mode '0644' and root ownership - maintain same permissions in Ansible file module
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External nginx dependency**: The cookbook declares dependency on external 'nginx' cookbook that may not be fetchable without Berksfile/Policyfile - need to identify actual nginx cookbook requirements or replace with Ansible nginx role
- **Metadata-only strategy**: Current setup is designed for testing metadata-only dependencies - migration needs to implement actual dependency resolution
- **Attribute translation**: Chef attributes need conversion to Ansible variables with appropriate precedence handling

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Simple redis installation
2. **simple-nginx cookbook** (moderate complexity) - Nginx installation with custom configuration and static content

### Assumptions

- The external 'nginx' cookbook dependency is a standard nginx installation cookbook that can be replaced with community nginx role
- Target systems have package managers compatible with the package names used (nginx, redis-server)
- The metadata-only dependency strategy testing purpose suggests this is a development/testing environment rather than production
- No complex nginx configuration beyond basic service setup is required based on the simple recipe content
- Redis configuration uses default settings since no custom configuration files are specified
- The cookbook supports both Ubuntu and CentOS but actual deployment targets are not specified
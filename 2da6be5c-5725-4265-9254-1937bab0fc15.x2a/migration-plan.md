# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible playbooks and roles. This is a low-complexity migration with straightforward package installations and service management, estimated timeline of 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, attribute-driven configuration

**cache**:
- Description: Redis cache server installation and service management as a local dependency
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis package installation and service management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 and root ownership - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **No secrets identified**: This repository contains no encrypted data bags, vault usage, or hardcoded credentials

### Technical Challenges

- **External dependency resolution**: The main cookbook depends on an external 'nginx' cookbook that is declared but not available without Berksfile/Policyfile - will need to implement nginx installation directly in Ansible or use community roles
- **Nested cookbook structure**: The cache cookbook is nested under cookbooks/ directory - will need to decide whether to convert to separate Ansible role or integrate into main playbook
- **Attribute inheritance**: Chef attributes system needs to be replaced with Ansible variables and defaults

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert to Ansible role with redis installation
2. **simple-nginx cookbook** (moderate complexity) - Convert main cookbook with nginx installation, file creation, and service management
3. **Integration testing** - Verify both components work together as intended

### Assumptions

- The external 'nginx' cookbook dependency will be replaced with direct nginx installation in Ansible rather than using a third-party Ansible role
- Target systems have package managers compatible with the specified platforms (apt for Ubuntu, yum/dnf for CentOS)
- The metadata-only dependency strategy testing purpose suggests this is a development/testing environment rather than production
- No complex nginx configuration is required beyond basic installation and service management
- Redis installation uses default configuration without custom settings
- The cookbook structure suggests this is a learning/testing repository rather than a production system
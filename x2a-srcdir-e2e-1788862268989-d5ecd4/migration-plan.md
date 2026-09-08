# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with moderate complexity due to external dependencies and service management requirements. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **redis-server**: Replace with ansible.builtin.package and redis role from Ansible Galaxy
- **cache (local)**: Convert to Ansible role with same functionality

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644, owner root:root - migrate to ansible.builtin.file module
- **Service management**: Both nginx and redis services use standard systemd management - convert to ansible.builtin.systemd
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in reviewed files
- **Package security**: Standard package manager installations without custom repositories or signing keys

### Technical Challenges

- **External dependency resolution**: The nginx cookbook dependency is declared but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible Galaxy role or create custom nginx role
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with proper defaults
- **Service ordering**: Ensure proper dependency ordering between package installation and service management in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package naming differences (redis-server vs redis)

### Migration Order

1. **cache** (low risk, simple Redis installation with minimal dependencies)
2. **simple-nginx** (moderate complexity, depends on cache module and external nginx cookbook)

### Assumptions

- The external nginx cookbook dependency provides standard nginx installation and configuration capabilities
- Redis installation follows standard package manager conventions on target platforms
- No custom nginx configuration files or templates exist beyond the simple index.html file
- Service management relies on standard systemd/init.d conventions
- No SSL/TLS certificates or advanced security configurations are required
- The metadata-only dependency strategy indicates this is a test/development environment rather than production
- Package repositories are available and accessible on target systems
- No custom compilation or source installations are required for nginx or redis
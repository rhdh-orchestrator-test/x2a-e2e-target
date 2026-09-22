# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward nature of the cookbooks and minimal external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate Redis installation to ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file creation with explicit mode (0644), owner (root), and group (root) settings need equivalent Ansible file module configuration
- **Service management**: Both nginx and redis services are enabled and started, requiring proper Ansible service module configuration
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Package security**: Standard package installation without version pinning may need security review for production environments

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile or Policyfile, requiring manual identification of the actual nginx cookbook requirements
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults and variable precedence
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to match Chef's resource convergence behavior
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS platforms using Ansible conditionals or platform-specific tasks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache module, external nginx dependency to resolve)

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook that provides basic nginx installation and configuration capabilities
- The target environment will have package managers (apt/yum) available for nginx and redis-server packages
- No custom nginx configuration files or templates are required beyond the basic installation
- The metadata-only dependency strategy indicates this is a test/example cookbook rather than a production-ready implementation
- No encrypted secrets, certificates, or complex security configurations are present in the unreviewed template or configuration files
- The Chef version requirement (>= 16.0) suggests modern Chef practices that should translate well to current Ansible versions
- Platform support is limited to Ubuntu 18.04+ and CentOS 7.0+, which aligns with current Ansible module compatibility
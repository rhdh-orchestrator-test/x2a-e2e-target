# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

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
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and nginx Ansible role or custom tasks
- **cache (local)**: Migrate internal cookbook to Ansible tasks for Redis installation

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module provides equivalent security
- **Package installation**: No version pinning observed - consider implementing version constraints in Ansible for security updates
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual resolution in Ansible
- **Attribute system migration**: Chef attributes system (default['nginx']['port']) needs conversion to Ansible variables with proper precedence
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain Chef's implicit resource ordering
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers (apt vs yum/dnf)

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis setup)
2. **simple-nginx cookbook** (moderate complexity, external nginx dependency, attribute system)

### Assumptions

- The external nginx dependency will be resolved through standard Ansible package management or community roles rather than requiring a specific Chef Supermarket cookbook equivalent
- The metadata-only dependency strategy indicates this is a test/example repository, so production hardening requirements may be minimal
- No complex template files or data bags are present based on the simple structure observed
- The target environment has standard package managers available (apt for Ubuntu, yum/dnf for CentOS)
- No custom Chef resources or libraries are in use that would require complex Ansible module development
- The current configuration is sufficient for the intended use case without additional nginx modules or complex caching configurations
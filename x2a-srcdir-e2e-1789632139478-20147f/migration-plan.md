# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks to Ansible roles with minimal complexity due to the straightforward nature of the configurations. Estimated timeline: 1-2 weeks for a single developer, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic nginx web server installation with service management and simple static content deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependency declarations and platform support
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform compatibility
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role dependency structure

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644, owner root:root - maintain in Ansible file module
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external 'nginx' dependency that may not be resolvable without Berksfile/Policyfile - need to identify and source appropriate Ansible nginx role or create custom implementation
- **Attribute system**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Platform compatibility**: Ensure Ansible playbooks maintain the same Ubuntu/CentOS support as declared in Chef metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and attribute usage)

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb is a standard nginx cookbook that can be replaced with community Ansible nginx role or custom implementation
- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in Chef metadata
- No additional Chef environments, data bags, or encrypted attributes exist beyond what's visible in the repository structure
- The metadata-only dependency strategy mentioned in README suggests this is a test/example repository rather than production code
- Redis configuration beyond basic installation is not required based on the simple implementation in the cache cookbook
- Static content deployment pattern (single index.html file) represents the full scope of web content management needed
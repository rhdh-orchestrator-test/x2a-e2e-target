# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two cookbooks (one main cookbook and one local dependency) to Ansible roles. This is a low-complexity migration with minimal dependencies and straightforward service management patterns.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low
**Risk Level**: Low

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified from the repository tree and confirmed via file exploration.

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, static HTML content deployment, configurable port and worker processes

- **cache**:
    - Description: Redis server installation and configuration for caching services
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis-server package installation, service management, automatic startup configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependency declarations and platform support definitions
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform compatibility specifications
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation describing metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role with same functionality

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - maintain same security posture in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No secrets, encrypted data bags, or credential management detected in the reviewed files

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external 'nginx' dependency that may not be fetchable without Berksfile/Policyfile - need to identify and replace with appropriate Ansible nginx role or create custom role
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker processes) to Ansible variables with appropriate defaults
- **Service ordering**: Ensure proper dependency ordering between cache and nginx services in Ansible playbooks

### Migration Order

1. **cache** (low risk, no external dependencies, simple package + service pattern)
2. **simple-nginx** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb will need to be replaced with a suitable Ansible nginx role from Ansible Galaxy or custom implementation
- Target systems will have package managers compatible with the package names used (nginx, redis-server)
- The cookbook is designed for testing purposes, so production hardening requirements may be minimal
- No complex configuration templates or advanced nginx features are required based on the simple recipe structure
- The metadata-only dependency strategy mentioned in documentation suggests this is a test/example cookbook rather than production infrastructure
- Platform support (Ubuntu 18.04+, CentOS 7.0+) indicates modern systemd-based service management
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

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

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Internal dependency that will be converted to Ansible role

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 with root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module provides equivalent security
- **Package installation**: No version pinning observed - consider implementing version constraints in Ansible for security compliance
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual resolution during migration
- **Attribute inheritance**: Chef attributes system needs mapping to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain Chef's implicit dependency management
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers and service systems

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, external nginx dependency, file management)

### Assumptions

- The external nginx dependency is available through standard package repositories on target systems
- No custom nginx configuration files beyond the simple index.html are required
- Redis configuration uses default settings (no custom redis.conf observed)
- The metadata-only strategy indicates this is a test/example cookbook rather than production infrastructure
- No encrypted data bags or Chef Vault secrets are present (none observed in reviewed files)
- Service startup order dependencies are handled implicitly by Chef and will need explicit task ordering in Ansible
- Platform-specific package names (nginx vs nginx-server, redis-server vs redis) may need conditional handling in Ansible
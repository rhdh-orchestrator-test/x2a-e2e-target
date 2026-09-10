# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two local cookbooks and external dependencies. The migration scope is relatively small but demonstrates key Chef patterns including local cookbook dependencies and external cookbook references. Estimated timeline: 1-2 weeks for a small team, with the main complexity being dependency resolution and testing.

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

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain same security baseline
- **Package installation**: No version pinning observed - consider implementing version constraints in Ansible for security compliance

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared but not locally available - will need to identify and replace with appropriate Ansible nginx role or create custom implementation
- **Attribute system migration**: Chef attributes system (default['nginx']['port']) needs conversion to Ansible variables with appropriate precedence
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, external dependency resolution required)
3. **Integration testing** (verify cookbook interdependencies work correctly in Ansible)

### Assumptions

- The external 'nginx' cookbook dependency will need to be replaced with a community Ansible role or custom implementation since it's not available in this repository
- Target systems have package managers compatible with the 'nginx' and 'redis-server' package names
- The metadata-only dependency strategy mentioned in README suggests this is a test/example repository rather than production code
- No secrets management or encrypted data bags are present in this simple example
- Default nginx configuration is sufficient (no custom nginx.conf templates observed)
- Redis configuration uses distribution defaults (no custom redis.conf observed)
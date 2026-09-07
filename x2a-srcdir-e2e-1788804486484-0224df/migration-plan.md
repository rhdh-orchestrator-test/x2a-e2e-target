# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

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

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on metadata.rb platform support declarations)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Migrate to inline Ansible tasks for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations match Chef behavior
- **Package installation**: No version pinning observed - consider adding version constraints in Ansible for production stability
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify the actual nginx cookbook requirements and translate to appropriate Ansible modules
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with proper precedence handling
- **Service ordering**: Implicit Chef resource ordering may need explicit Ansible task dependencies
- **Platform compatibility**: Ensure Ansible playbooks maintain the same Ubuntu/CentOS support matrix

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx main cookbook** (moderate complexity, depends on cache and external nginx dependency)

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook that provides basic nginx installation and configuration capabilities
- The target environment will have package managers (apt/yum) available for nginx and redis-server packages
- The current Chef cookbook is used in a test/development context given the "metadata-only" strategy mentioned in documentation
- No complex nginx configuration beyond basic service management is required, as evidenced by the simple recipe structure
- The static HTML content deployment pattern should be preserved in the Ansible migration
- Platform support requirements (Ubuntu 18.04+, CentOS 7+) should be maintained in the Ansible version
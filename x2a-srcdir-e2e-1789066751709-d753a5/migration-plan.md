# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup with two cookbooks demonstrating a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

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
- **cache (local)**: Internal dependency that will become a separate Ansible role

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644, owner root:root - maintain in Ansible file module
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Package security**: Standard package installation without version pinning - consider adding version constraints in Ansible

### Technical Challenges

- **Metadata-only dependency strategy**: The current setup declares external nginx dependency without Berksfile/Policyfile resolution - will need to implement proper Ansible Galaxy or requirements.yml dependency management
- **Attribute system migration**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with proper precedence
- **Cross-cookbook dependencies**: The simple-nginx cookbook depends on the cache cookbook - this relationship needs to be maintained through Ansible role dependencies
- **Platform support**: Explicit Ubuntu/CentOS support declarations need translation to Ansible platform conditionals

### Migration Order

1. **cache** (low risk, no external dependencies, simple package + service pattern)
2. **simple-nginx** (moderate complexity, depends on cache role, external nginx dependency, file management)

### Assumptions

- The external nginx dependency mentioned in metadata.rb refers to a community cookbook that provides additional nginx functionality beyond basic package installation
- The target environment will have internet access for package installation via apt/yum
- The metadata-only strategy implies this is a testing/development setup rather than production
- No custom nginx configuration files are required beyond the basic service setup
- The cache cookbook's redis installation uses default configuration without custom redis.conf
- Platform support (Ubuntu 18.04+, CentOS 7.0+) will be maintained in the Ansible version
- No encrypted secrets or sensitive data are present in the current configuration
- The simple HTML index page content can remain static in the migrated version
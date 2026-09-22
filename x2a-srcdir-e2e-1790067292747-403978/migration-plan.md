# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward web server and caching service configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx.nginx collection for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with community.general.redis or ansible.builtin.package modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible equivalents
- **Package installation**: No version pinning observed - consider implementing version constraints in Ansible for security compliance
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile - will need to identify correct Ansible Galaxy collection or role equivalent
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original cookbook metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache module and external nginx dependency)

### Assumptions

- The external nginx dependency referenced in metadata.rb is assumed to be the standard nginx package available in distribution repositories, as no specific version or source is specified
- The cookbook is designed for testing metadata-only dependency strategies, so production hardening configurations may be minimal
- No custom nginx configuration files or templates are present, suggesting basic default configuration is acceptable
- Redis configuration uses distribution defaults since no custom configuration files are specified
- The target environment has internet access for package installation from standard repositories
- No SSL/TLS certificates or advanced security configurations are required based on the simple test nature of the cookbooks
- The cookbook structure suggests this is a proof-of-concept or testing setup rather than production infrastructure
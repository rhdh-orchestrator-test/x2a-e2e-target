# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward web server and caching service configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes via attributes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis-server package installation, service management, basic cache infrastructure

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency and local cache dependency
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local)**: Internal dependency that will be migrated as a separate Ansible role

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Package sources**: Default package repositories used - consider pinning package versions in Ansible for security consistency

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolved via Berksfile or Policyfile - migration team must identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with appropriate defaults and validation
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and configuration sequence
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers and service systems

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity, depends on cache role, requires external nginx dependency resolution)

### Assumptions

- The external nginx dependency refers to a standard community nginx cookbook with basic installation and configuration capabilities
- The metadata-only strategy indicates this is a test/example repository, so production hardening requirements may be minimal
- No custom templates, files, or complex configurations exist beyond what was observed in the default recipes
- The target environment will use the same package names (nginx, redis-server) as the source Chef recipes
- No environment-specific configurations or data bags are required beyond the basic attributes observed
- The simple HTML content deployment pattern suggests this is for testing/demo purposes rather than production web content management
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration scope is minimal with two basic cookbooks providing web server and caching functionality. Estimated timeline: 1-2 weeks for a single developer, with low complexity due to straightforward package installation and service management patterns.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Internal dependency that will become a separate Ansible role

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - maintain in Ansible with ansible.builtin.file module
- **Service security**: No specific security hardening observed in current configuration
- **Vault/secrets management**: No encrypted data bags, vault usage, or credential patterns identified in the reviewed files

### Technical Challenges

- **Metadata-only strategy**: Current setup relies on metadata.rb declarations without Berksfile/Policyfile - Ansible equivalent will need explicit role dependencies in requirements.yml
- **Cross-cookbook dependencies**: The simple-nginx cookbook depends on the cache cookbook, requiring careful role dependency mapping in Ansible
- **Platform abstraction**: Chef's platform-specific package names may need explicit handling in Ansible for Ubuntu vs CentOS differences

### Migration Order

1. **cache** (low risk, no dependencies, simple package + service pattern)
2. **simple-nginx** (depends on cache role, moderate complexity with file creation and attributes)

### Assumptions

- The external 'nginx' dependency mentioned in metadata.rb is intended to be resolved through community cookbooks, but no Berksfile/Policyfile exists to specify the source
- The repository is designed for testing purposes rather than production deployment, given the simple configurations and "metadata-only" strategy mentioned in documentation
- Default nginx configuration is acceptable since no custom nginx.conf templates or advanced configuration management is present
- Redis server can use default configuration since no custom redis.conf management is implemented
- Target systems have internet access for package installation via standard package managers (apt/yum)
- The cookbook is intended to run with elevated privileges (root) based on file ownership patterns
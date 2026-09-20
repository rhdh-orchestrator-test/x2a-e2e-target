# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles. This is a low-complexity migration with straightforward package management and service configuration, estimated timeline of 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management and auto-start configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining simple-nginx cookbook with dependencies on cache and nginx
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port 80, www-data user, auto worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role with redis package management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file uses explicit 0644 permissions and root ownership - maintain in Ansible with ansible.builtin.file module
- **Service security**: No custom security configurations identified in the current implementation
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual resolution during migration
- **Platform compatibility**: Ensure Ansible playbooks maintain support for both Ubuntu and CentOS package managers (apt vs yum/dnf)
- **Service management**: Convert Chef service resources to appropriate Ansible service module calls with proper state management

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external nginx dependency will need to be resolved through Ansible Galaxy or custom role development since no Berksfile/Policyfile exists
- Target systems will have appropriate package managers available (apt for Ubuntu, yum/dnf for CentOS)
- The metadata-only dependency strategy mentioned in README suggests this is a test environment, so production considerations may be minimal
- No complex nginx configuration is required beyond basic service management and static content
- Redis configuration uses default settings without custom tuning requirements
- The cookbook structure suggests this is primarily for testing X2A Convertor functionality rather than production deployment
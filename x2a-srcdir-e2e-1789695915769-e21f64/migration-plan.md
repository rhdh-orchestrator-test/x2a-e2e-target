# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with minimal complexity due to the straightforward nature of the configurations. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

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

- **File permissions**: Static HTML file uses explicit mode 0644 with root ownership - maintain in Ansible file module
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No secrets or encrypted data identified in the current configuration files

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external nginx dependency that may not be resolvable without Berksfile/Policyfile - need to identify the actual nginx cookbook source or replace with direct package management
- **Attribute translation**: Convert Chef attributes to Ansible variables with appropriate defaults and variable precedence
- **Service ordering**: Ensure proper dependency ordering between cache and nginx services in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency)

### Assumptions

- The external nginx dependency referenced in metadata.rb is not critical to basic functionality since the recipe uses direct package installation
- Target systems will have package managers available (apt for Ubuntu, yum/dnf for CentOS)
- No custom nginx configuration files are required beyond the basic installation
- Redis default configuration is sufficient for the caching use case
- The metadata-only dependency strategy is for testing purposes and can be replaced with standard Ansible role dependencies
- No encrypted data bags, vault configurations, or complex templating requirements exist beyond what was observed in the source files
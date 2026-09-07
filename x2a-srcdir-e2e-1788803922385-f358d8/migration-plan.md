# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible playbooks and roles. This is a low-complexity migration with straightforward package installations and service management, estimated timeline of 1-2 weeks for a small team.

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
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Convert to Ansible role with redis package management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 with root ownership - maintain in Ansible file module
- **Service management**: Both nginx and redis services use standard enable/start actions - straightforward Ansible service module conversion
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **Dependency resolution**: The cookbook declares external nginx dependency that may not be fetchable without Berksfile/Policyfile - need to identify actual nginx cookbook requirements or replace with direct package management
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker_processes) to Ansible variables with appropriate defaults
- **Cross-cookbook dependencies**: The simple-nginx cookbook depends on the cache cookbook - structure as Ansible role dependencies or include_role tasks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and attribute usage)

### Assumptions

- The external nginx dependency referenced in metadata.rb is not critical to basic functionality since the recipe only uses standard package installation
- The cookbook is designed for testing purposes, so production hardening requirements may be minimal
- Platform support will target the same OS families (Ubuntu/CentOS) as specified in Chef metadata
- No complex template files or advanced Chef features are used beyond basic package/service/file resources
- The metadata-only dependency strategy mentioned in README suggests this is a simplified test case rather than a production cookbook
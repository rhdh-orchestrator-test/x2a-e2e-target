# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible playbooks and roles. The scope is relatively small with basic web server and caching functionality, making this a low-complexity migration suitable for completion within 1-2 weeks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

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

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis installation and configuration tasks

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible file module
- **Service security**: No specific security hardening identified in source cookbooks - consider adding security configurations during migration
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials identified in the reviewed files

### Technical Challenges

- **Dependency resolution**: The cookbook declares dependency on external 'nginx' cookbook that may not be fetchable without Berksfile/Policyfile - need to identify actual nginx cookbook requirements or replace with built-in Ansible modules
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker_processes) to Ansible variables with appropriate defaults and variable precedence
- **Service management**: Ensure proper service state management translation from Chef service resource to Ansible service module

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and static content deployment, resolve external nginx dependency

### Assumptions

- The external 'nginx' dependency declared in metadata.rb is not critical for basic functionality since the default recipe uses built-in package and service resources
- Target systems will have package managers available (apt for Ubuntu, yum/dnf for CentOS) as assumed by Chef package resources
- The cookbook is intended for testing purposes based on README documentation, so production-grade security hardening may not be required
- No complex templating or dynamic configuration beyond basic attributes is needed
- Service management follows standard systemd patterns on target platforms
- No custom nginx configuration files are required beyond the basic installation and static HTML content
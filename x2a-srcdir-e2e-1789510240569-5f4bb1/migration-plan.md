# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration scope is relatively straightforward with two cookbooks providing basic web server and caching functionality. Estimated timeline: 1-2 weeks for a small team, with low complexity due to minimal dependencies and straightforward service configurations.

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
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx.nginx collection for advanced configuration
- **redis-server**: Replace with community.general.redis module or ansible.builtin.package for basic installation
- **cache (local)**: Internal dependency that will be converted to an Ansible role

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External nginx dependency**: The cookbook declares a dependency on an external 'nginx' cookbook that is not present in the repository, requiring identification of equivalent Ansible nginx role or collection
- **Metadata-only strategy**: The current setup uses metadata declarations without actual dependency resolution (no Berksfile/Policyfile), which may indicate incomplete dependency management that needs to be addressed in Ansible
- **Attribute translation**: Chef attributes need to be converted to Ansible variables with proper precedence and scoping

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, handle external dependency resolution, migrate attribute system to Ansible variables

### Assumptions

- The external 'nginx' cookbook dependency mentioned in metadata.rb is not critical for basic functionality, as the recipes contain direct package installation commands
- Target systems will have package managers compatible with the 'package' resource (apt for Ubuntu, yum/dnf for CentOS)
- The metadata-only dependency strategy is for testing purposes and actual dependency resolution will be handled through Ansible Galaxy or custom roles
- No complex configuration templates or data bags are present beyond what was observed in the reviewed files
- Service names (nginx, redis-server) are consistent across target platforms or will be handled through Ansible platform-specific variables
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two lightweight cookbooks that provide basic web server and caching functionality. This is a low-complexity migration suitable for completion within 1-2 weeks, making it an excellent candidate for initial Ansible adoption or proof-of-concept work.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic Nginx web server installation and configuration with custom index page and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis installation and configuration tasks

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible Galaxy role or create custom tasks
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert Nginx setup with attribute handling and static file management

### Assumptions

- The nginx external dependency refers to a standard nginx installation rather than a complex cookbook with advanced configuration
- The target environment will have package managers (apt/yum) available for nginx and redis installation
- No custom nginx configuration files are required beyond the basic installation and static index page
- The metadata-only dependency strategy testing purpose suggests this is a development/testing environment rather than production
- Platform support (Ubuntu 18.04+, CentOS 7+) indicates modern systemd-based service management is available
- No complex inter-cookbook communication or shared state management is required beyond the simple dependency relationship
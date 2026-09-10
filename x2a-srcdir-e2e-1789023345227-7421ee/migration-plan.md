# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward web server and caching service configuration.

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
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain proper service security
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Package installation**: Standard package manager usage without custom repositories or signing key management

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolved via Berksfile or Policyfile - migration team must identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults and variable precedence
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and configuration sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Simple Redis installation with clear package and service management
2. **simple-nginx cookbook** (moderate complexity) - Nginx installation with custom content and external dependency resolution required

### Assumptions

- The external nginx dependency refers to a standard community nginx cookbook with basic installation and configuration capabilities
- The target environment has standard package managers (apt for Ubuntu, yum/dnf for CentOS) available
- No custom nginx compilation or advanced configuration features are required beyond basic web server functionality
- Redis configuration uses default settings and does not require custom configuration files or clustering setup
- The metadata-only dependency strategy indicates this is a test/example repository rather than production infrastructure
- No SSL/TLS configuration is required based on the simple HTTP-only setup observed
- The cookbook supports both Ubuntu and CentOS but actual deployment targets are not specified in the source
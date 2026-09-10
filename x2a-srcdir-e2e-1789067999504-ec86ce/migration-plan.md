# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves two cookbooks with basic web server and caching functionality. This is a low-complexity migration suitable for completion within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic Nginx web server installation and configuration with custom index page and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support declarations

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared but not locally available - will need to implement nginx installation directly in Ansible or source appropriate role from Ansible Galaxy
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Cross-cookbook dependencies**: The main cookbook depends on the local 'cache' cookbook - ensure proper role dependencies in Ansible

### Migration Order

1. **cache cookbook** (low risk, no dependencies) - Migrate Redis installation and service management first
2. **simple-nginx cookbook** (moderate complexity) - Migrate after cache role is complete to maintain dependency order
3. **Integration testing** - Verify both roles work together and maintain the same functionality as the original Chef cookbooks

### Assumptions

- The external 'nginx' cookbook dependency will be replaced with direct Ansible nginx installation rather than sourcing a third-party role
- Current Chef attribute values (port 80, www-data user, auto worker processes) represent the desired production configuration
- The simple HTML index page content should be preserved exactly as specified
- Both Ubuntu and CentOS platform support requirements will be maintained in the Ansible implementation
- No additional Chef environments, data bags, or encrypted attributes exist beyond what's visible in this repository structure
- The repository represents a complete, self-contained cookbook set for testing purposes rather than part of a larger Chef infrastructure
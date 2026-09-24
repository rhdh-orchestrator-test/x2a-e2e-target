# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **User context**: Nginx configured to run as www-data user - ensure proper user/group configuration in Ansible playbooks
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual dependency resolution in Ansible
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with proper precedence
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache** (low risk, no external dependencies) - Redis installation and service management
2. **simple-nginx** (moderate complexity) - Nginx installation with custom configuration and static content

### Assumptions

- The external nginx dependency mentioned in metadata.rb refers to a standard nginx cookbook from Chef Supermarket, not a custom implementation
- The target environment will have package managers (apt/yum) available for nginx and redis installation
- The metadata-only dependency strategy indicates this is a test/example cookbook, suggesting simplified production requirements
- No complex templating or dynamic configuration is required beyond the basic attributes defined
- The cookbook is designed for testing purposes (as indicated in README), so production-grade features like SSL, load balancing, or advanced caching configurations are not expected
- Platform support will be maintained for Ubuntu 18.04+ and CentOS 7.0+ as specified in the original metadata
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable attributes for port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 with root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Package sources**: Default package repositories used - consider package verification and signing in Ansible implementation

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual dependency resolution in Ansible
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults and validation
- **Service ordering**: Ensure proper dependency ordering between package installation and service management in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS with appropriate package name variations

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis setup)
2. **simple-nginx cookbook** (moderate complexity, external nginx dependency, attribute management)

### Assumptions

- The external nginx dependency will be resolved through standard package repositories rather than a specific Chef cookbook
- The metadata-only dependency strategy indicates this is a test/example repository rather than production code
- No custom nginx configuration files are required beyond the basic service setup
- Redis configuration uses default settings without custom configuration files
- The target environment has access to standard package repositories for nginx and redis-server
- No SSL/TLS certificates or advanced security configurations are required
- The simple HTML index page content can be managed as a static file in Ansible
- Platform-specific package names (nginx vs nginx-server, redis-server vs redis) will be handled through Ansible conditionals
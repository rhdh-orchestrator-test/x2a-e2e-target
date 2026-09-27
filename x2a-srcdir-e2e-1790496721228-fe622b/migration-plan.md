# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with moderate complexity due to external dependencies and service management requirements. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to separate Ansible role with proper role dependencies

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 - ensure Ansible file module maintains proper permissions
- **Service user**: Nginx configured to run as www-data user - verify user exists or create in Ansible playbook
- **No secrets management**: No encrypted data bags, vault usage, or credential patterns detected in reviewed files
- **Basic security posture**: Default configurations without hardening - opportunity to enhance security during migration

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared but not fetchable without Berksfile/Policyfile - need to identify correct nginx role from Ansible Galaxy or create custom role
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS with appropriate package name handling

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis setup)
2. **simple-nginx cookbook** (moderate complexity, external nginx dependency, file management)

### Assumptions

- The external nginx dependency can be satisfied by community nginx roles or custom implementation
- Target systems have package managers (apt/yum) available and configured
- No complex nginx configuration beyond basic service setup is required
- Redis default configuration is sufficient for the cache use case
- No custom templates or complex file structures exist beyond what was reviewed
- The metadata-only strategy indicates this is a test/example cookbook rather than production-critical infrastructure
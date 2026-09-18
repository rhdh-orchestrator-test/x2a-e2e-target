# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup designed for testing metadata-only dependency strategies. The migration involves two cookbooks with basic web server and caching functionality. This is a low-complexity migration suitable for completion within 1-2 weeks, making it an excellent candidate for establishing migration patterns and team processes.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic Nginx web server installation with service management and simple static content deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate Redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package module and redis configuration management

### Security Considerations

- **File permissions**: Static HTML file creation uses explicit mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible equivalents
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Default configurations**: Using default nginx and redis configurations - consider security hardening during migration

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify correct Ansible Galaxy collection or create custom nginx role
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain Chef's implicit resource ordering
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package naming differences

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Simple Redis installation and service management
   - Good starting point to establish migration patterns
2. **simple-nginx cookbook** (moderate complexity)
   - Depends on cache cookbook completion
   - Requires external nginx dependency resolution
   - File creation and attribute handling

### Assumptions

- The external 'nginx' dependency refers to a standard nginx installation cookbook - specific version and source need identification
- Current deployment uses default nginx and redis configurations - production environments may require additional security hardening
- The metadata-only strategy suggests this is a test/development environment - production migration may reveal additional complexity
- No custom templates, files, or complex configurations are present beyond what's visible in the basic recipe structure
- Platform support is limited to Ubuntu 18.04+ and CentOS 7.0+ as declared in metadata - other distributions may require additional testing
- No environment-specific configurations (staging, production) are present in this simplified test setup
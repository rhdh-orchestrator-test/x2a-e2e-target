# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate basic web server and caching functionality. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic nginx web server installation and configuration with custom index page and service management
- Path: . (root level)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup, basic caching infrastructure

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port (80), user (www-data), and worker processes
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with Ansible redis role from community collections or custom tasks

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Package installation**: Standard package manager usage without custom repositories or signing key management

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata.rb but no Berksfile or Policyfile exists, suggesting this cookbook expects nginx to be available through other means - need to identify the actual nginx cookbook source or replace with direct Ansible nginx management
- **Metadata-only strategy**: The README indicates this is a test cookbook for "metadata-only dependency strategy" which may not reflect production dependency management patterns
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need to be converted to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Simple redis installation with clear package and service management
2. **simple-nginx cookbook** (moderate complexity) - Depends on cache module and external nginx dependency resolution

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb will need to be resolved through Ansible Galaxy roles or custom implementation since no dependency management files (Berksfile/Policyfile) are present
- The target environment has standard package managers (apt for Ubuntu, yum/dnf for CentOS) available for nginx and redis installation
- The cookbook structure suggests this is a testing/example repository rather than production code, which may simplify migration requirements
- No custom nginx configuration files are managed beyond the basic service setup, so standard Ansible nginx modules should be sufficient
- The static HTML content can be directly translated to Ansible's file module without template complexity
- No encrypted secrets or vault integration exists, simplifying the security migration aspect
- Platform support will be maintained for Ubuntu 18.04+ and CentOS 7+ as specified in the original metadata
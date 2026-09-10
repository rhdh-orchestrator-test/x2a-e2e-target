# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward nature of the cookbooks and minimal external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package module and redis configuration management

### Security Considerations

- **File permissions**: The nginx index.html file uses explicit mode '0644' with root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Network security**: Default nginx configuration uses port 80 - consider SSL/TLS configuration in Ansible migration

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify the specific nginx cookbook version and features used
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with proper precedence
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers (apt vs yum/dnf)

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache, external nginx dependency to resolve)

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook from Chef Supermarket - specific version and features need verification
- The metadata-only strategy suggests this is a test/example repository rather than production code
- No custom templates, files, or complex configurations beyond the basic recipes reviewed
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ as specified in metadata
- No environment-specific configurations or Hiera-equivalent data structures are present
- The cache cookbook's redis installation uses default configuration without custom redis.conf templates
- No SSL/TLS certificates or encrypted communications are configured in the current setup
- The nginx configuration relies on default package installation without custom virtual hosts or advanced features
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis cache server installation and service management as a local dependency
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server package installation, service management, basic configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependency declarations on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate Redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with Ansible redis role from community collections or custom tasks

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for the index.html file - ensure Ansible tasks maintain proper file ownership and permissions
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible equivalents
- **No vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Default configurations**: Using default service configurations which may need security hardening in Ansible implementation

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile or Policyfile - need to identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need to be converted to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to handle service dependencies between nginx and cache components
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS platforms with appropriate package name variations

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache, requires external nginx dependency resolution)

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook from Chef Supermarket - specific version and features need to be identified during migration
- The metadata-only strategy suggests this is a test/example cookbook - production usage patterns may differ
- Default Redis and Nginx configurations are acceptable for the target environment - no custom configuration files or templates were found
- The cookbook is designed for basic web server functionality - advanced nginx features (SSL, virtual hosts, load balancing) are not implemented
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ - newer OS versions may require testing and validation
- No custom Chef resources or complex logic beyond basic package/service/file management
- The absence of Berksfile or Policyfile suggests dependencies are managed externally or this is a standalone test cookbook
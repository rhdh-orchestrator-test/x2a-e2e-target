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

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 and root ownership - ensure Ansible playbook maintains proper file permissions
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations during migration
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile or Policyfile - need to identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables with appropriate precedence
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external 'nginx' dependency refers to a standard community nginx cookbook with basic installation and configuration capabilities
- The target environment has package managers (apt/yum) available for nginx and redis installation
- No custom nginx configuration files or templates are required beyond the basic setup shown
- The metadata-only strategy indicates this is a test/example repository rather than production infrastructure
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ as specified in metadata
- No complex nginx virtual host configurations or SSL/TLS setup is required based on the simple recipe content
- Redis configuration uses default settings without custom configuration files or security hardening
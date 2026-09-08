# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service management, static file deployment, attribute-driven configuration

- **cache**:
    - Description: Redis cache server installation and service management as a local dependency
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package module and redis configuration via ansible.builtin.template if needed

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit permissions (0644, root:root) - ensure Ansible playbooks maintain proper file ownership and permissions
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Network security**: Default nginx configuration uses port 80 - consider SSL/TLS configuration in Ansible migration

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile or Policyfile - need to identify the specific nginx cookbook version and features used
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management in Ansible
- **Platform compatibility**: Cookbook supports both Ubuntu and CentOS - Ansible playbooks need conditional logic for package manager differences

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache module, external nginx dependency to resolve)

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook from Chef Supermarket - specific version and configuration requirements need clarification
- The metadata-only strategy suggests this is a test/example repository - production usage patterns may differ
- No custom templates, files, or complex configurations are present beyond what's visible in the default recipes
- The target environment will have internet access for package installation via apt/yum
- No custom nginx configuration beyond basic service management is required - the cookbook only creates a simple index.html file
- Redis configuration uses default settings - no custom redis.conf or security configurations are specified
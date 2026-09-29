# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup with 2 cookbooks that demonstrate basic web server and caching infrastructure. The migration is relatively straightforward due to the simple nature of the cookbooks, with an estimated timeline of 1-2 weeks for a small team. The main complexity lies in handling the external nginx dependency and ensuring proper service management translation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic Nginx web server installation with custom index page and configurable attributes for port, user, and worker processes
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on local 'cache' cookbook and external 'nginx' cookbook
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port 80, www-data user, auto worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on metadata.rb platform support declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules or nginx role from Ansible Galaxy
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration

### Security Considerations

- **Service Management**: Both cookbooks manage system services (nginx, redis-server) - ensure proper systemd/init system handling in Ansible
- **File Permissions**: Static file creation uses explicit ownership (root:root) and permissions (0644) - maintain same security posture
- **Vault/secrets management**: No secrets or credentials identified in the reviewed files - cookbooks use default configurations only

### Technical Challenges

- **External Dependency Resolution**: The main cookbook depends on an external 'nginx' cookbook not present in the repository - will need to identify and replace with appropriate Ansible nginx role or custom tasks
- **Attribute Translation**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Service State Management**: Chef's service resource actions (enable, start) need proper translation to Ansible service module equivalents
- **Package Manager Abstraction**: Chef's package resource abstracts between apt/yum - ensure Ansible playbooks handle multi-platform package management correctly

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity due to external nginx dependency and attribute system)

### Assumptions

- The external 'nginx' cookbook dependency will be replaced with a suitable Ansible nginx role from Galaxy or custom implementation
- Target systems will have appropriate package managers (apt for Ubuntu, yum/dnf for CentOS/RHEL)
- No custom Chef resources or complex logic beyond basic package/service/file management
- The metadata-only dependency strategy mentioned in README suggests this is a test/example repository rather than production code
- No encrypted data bags, Chef Vault, or other Chef-specific secret management in use
- Service management assumes systemd on target platforms (Ubuntu 18.04+, CentOS 7+)
- No complex template rendering or dynamic configuration generation beyond basic attribute substitution
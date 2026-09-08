# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef-based infrastructure configuration with two cookbooks managing web server and caching services. The migration involves converting Chef recipes to Ansible playbooks and roles, with minimal complexity due to the straightforward service management patterns. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Nginx web server installation and configuration with basic service management and custom index page deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules
- **cache (local)**: Convert to Ansible role with redis package and service management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- File permissions: Static HTML file created with explicit mode 0644, owner root:root - migrate to ansible.builtin.file module with same permissions
- Service management: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- No vault/secrets management: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **Dependency resolution**: The root cookbook depends on an external 'nginx' cookbook that may not be available without Berksfile/Policyfile - need to identify and replace this dependency
- **Attribute inheritance**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Service ordering**: Ensure proper dependency ordering between cache and web server services in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert redis installation and service management
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, resolve external nginx cookbook dependency, migrate attribute system

### Assumptions

- The external 'nginx' cookbook dependency is not present in this repository and will need to be resolved or replaced during migration
- Target systems have package managers compatible with the current package installation approach (apt for Ubuntu, yum/dnf for CentOS)
- The metadata-only dependency strategy mentioned in README suggests this is a test/example repository rather than production infrastructure
- No complex templating or advanced Chef features are in use based on the simple recipe structures observed
- Service management follows standard systemd patterns on the target platforms
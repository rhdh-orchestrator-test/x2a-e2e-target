# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching infrastructure provisioning. The scope is relatively small but demonstrates key Chef-to-Ansible migration patterns including local dependencies, package management, and service configuration.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Nginx web server installation and configuration with basic HTML content serving and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup, basic caching infrastructure

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with Chef version requirements, platform support, and dependency declarations
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform compatibility definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy and cookbook purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **redis-server**: Replace with ansible.builtin.package and redis role from Ansible Galaxy
- **cache (local)**: Convert to Ansible role with same Redis functionality

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - maintain in Ansible with ansible.builtin.file module
- **Service security**: Both nginx and redis services run with default configurations - review security hardening requirements for production deployment
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or credential management detected in current implementation - all configurations use default values

### Technical Challenges

- **Metadata-only dependencies**: Current setup relies on metadata.rb declarations without Berksfile or Policyfile - will need to establish clear Ansible role dependencies in meta/main.yml
- **Local cookbook dependency**: The cache cookbook is embedded locally - convert to separate Ansible role and establish proper role dependencies
- **Attribute inheritance**: Chef attributes system needs mapping to Ansible variables with proper precedence and default value handling
- **Service management**: Both cookbooks use Chef service resource - ensure systemd compatibility in target Ansible roles

### Migration Order

1. **cache cookbook** (low risk, no dependencies) - Convert Redis installation and service management to standalone Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and static content deployment, establishing dependency on converted cache role

### Assumptions

- Target systems will have systemd for service management (Ubuntu 18.04+ and CentOS 7+ both use systemd)
- External nginx dependency will be satisfied by standard package repositories on target systems
- Redis server package naming conventions remain consistent across target platforms (redis-server)
- No custom nginx configuration templates are required beyond basic installation and service management
- Static HTML content deployment pattern will remain the same (single index.html file)
- Default nginx user (www-data) and configuration attributes are acceptable for target environment
- No SSL/TLS configuration or advanced nginx features are required in initial migration
- Chef version requirements (>= 16.0) indicate modern cookbook patterns that should translate well to current Ansible practices
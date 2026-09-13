# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with moderate complexity due to external dependencies and service management requirements. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup, basic cache server functionality

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local)**: Convert to Ansible role dependency in requirements.yml or include as part of the same playbook structure

### Security Considerations

- **File permissions**: The cookbook creates files with explicit mode '0644' and ownership (root:root) - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd/init service handling in target environment
- **Web content security**: Static HTML content is deployed to /var/www/html - consider implementing proper web root permissions and SELinux contexts if applicable
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files - migration should maintain this clean security posture

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to implement proper Ansible Galaxy or package manager dependency resolution
- **Attribute system migration**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with proper precedence and default value handling
- **Service dependency ordering**: Ensure proper task ordering when both nginx and cache services need to be configured and started
- **Platform compatibility**: Cookbook supports both Ubuntu and CentOS - Ansible playbooks must handle package name differences and service management variations between distributions

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity, depends on cache role, external nginx dependency to resolve)

### Assumptions

- The external nginx dependency can be satisfied through system package managers or Ansible Galaxy collections rather than requiring a specific Chef cookbook equivalent
- The target environment has internet access for package installation or appropriate local repositories are configured
- The metadata-only dependency strategy mentioned in documentation refers to testing scenarios and won't require special handling in the Ansible migration
- Default nginx configuration will be sufficient, as no custom nginx.conf templates or advanced configuration files were found in the source
- Redis will be used with default configuration, as no custom redis.conf or advanced Redis settings were detected
- The cookbook's testing purpose suggests this is a development/testing environment rather than production, allowing for simplified migration approach
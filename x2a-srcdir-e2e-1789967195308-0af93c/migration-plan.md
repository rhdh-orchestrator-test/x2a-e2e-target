# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with moderate complexity due to external dependencies and service management requirements. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, basic HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup, basic cache server functionality

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with Chef version requirements and platform support declarations
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform compatibility specifications
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy and cookbook structure

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management

### Security Considerations

- **File permissions**: The cookbook creates files with explicit mode '0644' and ownership (root:root) - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd integration in Ansible
- **Web content security**: Static HTML content is deployed to /var/www/html - ensure proper web directory permissions and ownership in Ansible implementation
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The main cookbook depends on an external 'nginx' cookbook that is not present in the repository - will need to implement nginx configuration directly in Ansible or source appropriate community roles
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need to be converted to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to handle package installation before service management
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS platforms using Ansible's platform-specific conditionals

### Migration Order

1. **cache cookbook** (low risk, simple Redis installation with no external dependencies)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external 'nginx' cookbook dependency will need to be replaced with direct Ansible implementation or community roles since it's not available in the current repository
- Target systems have internet access for package installation via apt/yum package managers
- The metadata-only dependency strategy mentioned in documentation suggests this is a test/example cookbook rather than production code
- Default nginx configuration will be sufficient, as no custom nginx.conf templates are present in the source
- Redis will use default configuration since no custom redis.conf management is implemented
- The cookbook supports Chef 16.0+ but migration timeline assumes modern Ansible (2.9+) capabilities
- No complex Chef resources or custom providers are used that would require special Ansible module development
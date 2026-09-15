# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution for the external nginx cookbook.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes via attributes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules or nginx role from Ansible Galaxy
- **cache (local)**: Convert to Ansible tasks for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 - ensure Ansible tasks maintain proper file permissions
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible equivalents
- **User context**: Nginx user configuration (www-data) needs to be properly handled in Ansible playbooks
- **No vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared in metadata but not available locally - will need to identify appropriate Ansible nginx role or create custom tasks
- **Attribute translation**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering when both nginx and cache services are managed
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible tasks
2. **simple-nginx cookbook** (moderate complexity) - Handle nginx installation, configuration, and static content deployment
3. **Integration testing** - Verify both services work together and maintain original functionality

### Assumptions

- The external 'nginx' cookbook dependency will be replaced with either an Ansible Galaxy nginx role or custom tasks - the specific nginx cookbook version and features are unknown
- Platform-specific package names (nginx vs nginx-server, redis-server vs redis) may need adjustment based on target OS
- The metadata-only strategy suggests this is a test/example repository - production usage patterns may differ
- No complex nginx configuration beyond basic installation is required based on the simple recipe content
- Redis configuration uses default settings - no custom redis.conf management detected
- No SSL/TLS configuration or advanced security hardening is currently implemented
- The cookbook supports Chef 16.0+ but Ansible version requirements are not specified
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both a main cookbook and a local dependency, making it an excellent candidate for a straightforward Ansible migration with minimal complexity.

**Timeline Estimate**: 1-2 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **simple-nginx**:
    - Description: Simple nginx web server cookbook with basic package installation, service management, and static content deployment
    - Path: . (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service enablement and startup, custom index.html creation, attribute-driven configuration for port, user, and worker processes

- **cache**:
    - Description: Redis cache server cookbook providing caching services as a local dependency
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis-server package installation, service management, basic cache functionality

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external) cookbooks, platform support for Ubuntu 18.04+ and CentOS 7+
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port: 80, user: www-data, worker_processes: auto)
- `README.md`: Documentation explaining the metadata-only dependency strategy for X2A Convertor testing

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.redis module for advanced configuration
- **cache (local dependency)**: Convert to Ansible role dependency or include within the main playbook

### Security Considerations
- **File permissions**: The cookbook creates `/var/www/html/index.html` with mode '0644' and root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the current codebase
- **Static content**: Custom index.html content is hardcoded - consider templating for dynamic environments

### Technical Challenges
- **Dependency resolution**: The cookbook depends on an external 'nginx' cookbook that is "declared but not fetchable without Berks/Policy" - need to identify the actual nginx cookbook requirements or implement nginx configuration directly
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need to be converted to Ansible variables with appropriate defaults
- **Service ordering**: Ensure proper dependency ordering between nginx and cache services in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers (apt vs yum/dnf)

### Migration Order
1. **cache cookbook** (low risk, no external dependencies) - Convert redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, service management, and file creation to Ansible playbook, resolve external nginx cookbook dependency

### Assumptions
- The external 'nginx' cookbook dependency mentioned in metadata.rb is not critical for basic functionality since the recipe directly uses the 'nginx' package
- The target environment has internet access for package installation via apt/yum repositories
- The cookbook is intended for development/testing purposes based on the "X2A Convertor" testing context mentioned in README
- Default nginx configuration is sufficient - no custom nginx.conf templates or advanced configuration required
- Redis default configuration is acceptable - no custom redis.conf or clustering requirements
- The metadata-only dependency strategy is a testing pattern and not a production requirement that needs to be preserved in Ansible
- File system structure follows standard Linux conventions (/var/www/html for web content)
- Services should be enabled and started immediately after installation (no delayed startup requirements)
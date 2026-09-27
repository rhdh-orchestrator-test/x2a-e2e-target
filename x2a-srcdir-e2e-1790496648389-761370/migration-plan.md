# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two modules that demonstrate a metadata-only dependency strategy. The migration scope is relatively small with basic web server and caching functionality, making this a low-complexity migration suitable for completion within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `attributes/default.rb`: Default nginx configuration attributes (port 80, www-data user, auto worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy and cookbook purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Internal dependency that will be migrated as part of this repository
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The nginx index.html file uses explicit mode 0644 with root ownership - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd integration in Ansible
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual resolution of the nginx cookbook functionality
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper dependency chain between cache and nginx services in Ansible playbooks

### Migration Order

1. **cache** (low risk, no external dependencies) - Redis installation and service management
2. **simple-nginx** (moderate complexity) - Nginx installation with dependency on cache module, custom configuration, and static content

### Assumptions

- The external nginx dependency referenced in metadata.rb contains standard nginx cookbook functionality that can be replaced with built-in Ansible modules
- Target systems have package managers compatible with the package names used (nginx, redis-server)
- The metadata-only dependency strategy indicates this is a test/example repository rather than production code
- No complex nginx configuration beyond basic service setup is required, as evidenced by the simple recipe content
- Redis configuration uses default settings since no custom configuration files or templates were found
- The cookbook supports both Ubuntu and CentOS, but specific package name differences between distributions are not handled in the current Chef code
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef-based infrastructure setup with two cookbooks managing web server and caching services. The migration involves converting basic service management patterns from Chef to Ansible, with low complexity due to the straightforward nature of the configurations. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic service management and static content deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert redis installation and service management to Ansible equivalents using ansible.builtin.package and ansible.builtin.service

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain proper startup behavior
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify if this refers to a community cookbook or custom implementation
- **Attribute-driven configuration**: The nginx attributes (port, user, worker_processes) need to be converted to Ansible variables with appropriate defaults
- **Cross-cookbook dependencies**: The simple-nginx cookbook depends on the cache cookbook - ensure proper Ansible role dependencies or playbook ordering

### Migration Order

1. **cache** (low risk, no dependencies) - Simple redis installation and service management
2. **simple-nginx** (moderate complexity) - Web server setup with static content and attribute-driven configuration, depends on cache module

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb is assumed to be a standard community cookbook for nginx installation, as no custom nginx cookbook is present in the repository
- The target environment supports both Ubuntu and CentOS package managers (apt/yum) as indicated by the platform support declarations
- The static HTML content deployment pattern suggests this is a basic web server setup rather than a complex application deployment
- No advanced nginx configuration (virtual hosts, SSL, reverse proxy) is required based on the simple recipe content
- Redis is used as a basic cache service without clustering or advanced configuration requirements
- The metadata-only dependency strategy mentioned in README suggests this is a test/example repository rather than production infrastructure
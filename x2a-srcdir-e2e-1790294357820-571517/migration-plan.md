# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on maintaining the dependency relationship and basic web server functionality. The scope is relatively small with an estimated timeline of 1-2 weeks for complete migration including testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis collection for advanced Redis management
- **cache (local)**: Convert internal cookbook dependency to Ansible role dependency using meta/main.yml

### Security Considerations

- **File permissions**: The cookbook creates files with explicit mode '0644' and ownership (root:root) - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper systemd service configuration in target environment
- **Web content security**: Static HTML file deployment needs proper web root permissions and SELinux context if applicable
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files - this is a low-security-risk migration

### Technical Challenges

- **Metadata-only dependencies**: The cookbook declares an external 'nginx' dependency without Berksfile or Policyfile resolution - migration must handle this external dependency through Ansible Galaxy or package management
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with proper defaults and precedence
- **Cross-cookbook dependencies**: The simple-nginx cookbook depends on the cache cookbook - this relationship must be preserved through Ansible role dependencies
- **Platform compatibility**: Cookbook supports both Ubuntu and CentOS - Ansible playbooks must handle package name differences (nginx vs nginx, redis-server vs redis)

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert to standalone Ansible role with Redis installation and service management
2. **simple-nginx cookbook** (moderate complexity) - Convert to Ansible role with proper dependency on cache role and external nginx package handling
3. **Integration testing** - Validate role dependencies and cross-platform compatibility on Ubuntu and CentOS targets

### Assumptions

- The external 'nginx' dependency declared in metadata.rb is intended to be resolved through system package management rather than a specific Chef cookbook
- The target environment has internet access for package installation via apt/yum repositories
- The metadata-only dependency strategy is a testing pattern and production deployments would use proper dependency resolution
- Default nginx configuration is sufficient - no custom nginx.conf templates or advanced configuration blocks are required
- Redis server requires only basic installation with default configuration - no clustering, persistence, or security configuration needed
- The cookbook structure suggests this is a development/testing environment rather than production infrastructure
- Platform support is limited to the declared Ubuntu 18.04+ and CentOS 7+ - no Windows or other Unix variants need consideration
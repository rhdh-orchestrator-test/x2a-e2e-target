# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching infrastructure. The migration complexity is low due to the straightforward nature of the cookbooks, with an estimated timeline of 1-2 weeks for complete conversion and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, custom HTML content deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic caching infrastructure

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining simple-nginx cookbook with dependencies on cache and nginx
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis installation and configuration tasks
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for the index.html file - ensure Ansible file module maintains proper ownership and permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **No secrets identified**: The current implementation contains no hardcoded credentials, encrypted data bags, or certificate references

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external nginx dependency that is not fetchable without Berksfile/Policyfile - need to identify the actual nginx cookbook requirements and replace with appropriate Ansible modules or roles
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker_processes) to Ansible variables with proper defaults and templating
- **Service ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and configuration sequence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and content deployment, resolve external nginx dependency requirements

### Assumptions

- The external nginx dependency referenced in metadata.rb is a standard nginx cookbook that can be replaced with built-in Ansible modules
- The target environment has package managers (apt/yum) available for nginx and redis-server packages
- The cookbook is intended for testing purposes as indicated by the README, so production-grade features like SSL, advanced configuration, or monitoring may not be required
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ as declared in the metadata
- No custom templates, files, or complex configuration management beyond the basic setup shown in the recipes
- The metadata-only dependency strategy mentioned in the README refers to Chef-specific dependency resolution and does not impact the Ansible migration approach
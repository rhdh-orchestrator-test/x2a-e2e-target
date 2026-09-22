# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that provide basic web server and caching functionality. The migration scope is relatively small but demonstrates key Chef patterns including local dependencies and external cookbook references. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Basic Nginx web server installation with service management and simple static content deployment
    - Path: . (root directory)
    - Technology: Chef
    - Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

- **cache**:
    - Description: Redis server installation and configuration for caching functionality
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation describing metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules
- **cache (local)**: Migrate to Ansible role with redis installation and configuration tasks

### Security Considerations
- **File permissions**: Static HTML file creation uses explicit mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **No vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files

### Technical Challenges
- **External dependency resolution**: The 'nginx' cookbook dependency is declared in metadata but not available locally - will need to identify appropriate Ansible equivalent or create custom nginx configuration
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence

### Migration Order
1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and attribute configuration)

### Assumptions
- The external 'nginx' cookbook dependency provides standard nginx installation and configuration capabilities that can be replaced with Ansible nginx modules or custom tasks
- The target environment has package managers (apt/yum) available for nginx and redis-server packages
- The cookbook is intended for testing metadata-only dependency strategies, suggesting this may be a proof-of-concept rather than production code
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ based on metadata declarations
- No complex nginx configuration beyond basic service setup is required, as evidenced by the simple default recipe
- The static HTML content deployment pattern suggests this is a basic web server setup rather than a complex application deployment
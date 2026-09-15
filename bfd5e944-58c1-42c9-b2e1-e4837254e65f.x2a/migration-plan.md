# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching infrastructure. The migration is relatively straightforward due to the simple nature of the cookbooks, with an estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, basic HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role dependency in requirements.yml or include as part of the same playbook

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for the HTML index file - ensure Ansible file module maintains proper ownership and permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **No secrets identified**: The current cookbooks do not contain hardcoded credentials, encrypted data bags, or certificate references

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external nginx dependency that is not fetchable without Berksfile/Policyfile - need to identify the actual nginx cookbook requirements and replace with appropriate Ansible modules or roles
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker processes) to Ansible variables with proper defaults and variable precedence
- **Service ordering**: Ensure proper task ordering when both nginx and cache services need to be configured together

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, service management, and file deployment, resolve external nginx dependency requirements
3. **Integration testing** - Validate that both roles work together and maintain the same functionality as the original Chef cookbooks

### Assumptions

- The external nginx dependency referenced in metadata.rb is a standard nginx cookbook that can be replaced with built-in Ansible modules or community roles
- The target environment has package managers (apt/yum) available for nginx and redis-server packages
- The cookbook is designed for testing purposes, so production-grade features like SSL, advanced configuration, or monitoring may not be required in the initial migration
- No custom templates or complex configuration files are needed beyond the basic setup shown in the recipes
- The metadata-only dependency strategy mentioned in the README suggests this is part of a larger testing framework that may not require full production migration
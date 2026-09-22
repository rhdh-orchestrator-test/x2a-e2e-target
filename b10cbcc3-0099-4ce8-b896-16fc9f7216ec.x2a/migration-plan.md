# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching infrastructure. The migration complexity is low due to the straightforward nature of the cookbooks, with an estimated timeline of 1-2 weeks for a small team.

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
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local)**: Convert to Ansible role dependency in requirements.yml or include as part of the same playbook

### Security Considerations

- **File permissions**: The cookbook creates /var/www/html/index.html with explicit mode 0644 - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **User context**: Nginx configuration references www-data user - ensure proper user/group management in target environment
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with proper defaults
- **Service dependency ordering**: Ensure proper task ordering when both nginx and cache services need to be configured together
- **Platform compatibility**: Cookbook supports both Ubuntu and CentOS - Ansible playbooks need conditional logic for package manager differences (apt vs yum/dnf)

### Migration Order

1. **cache** (low risk, no external dependencies) - Simple Redis installation with minimal configuration
2. **simple-nginx** (moderate complexity) - Nginx installation with custom content and attribute-driven configuration, depends on cache module

### Assumptions

- The external nginx dependency referenced in metadata.rb is the standard community nginx cookbook - specific version and required features need clarification
- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Redis and nginx packages are available in the target environment's package repositories
- The /var/www/html directory structure is appropriate for the target nginx configuration
- No additional Chef resources or advanced cookbook features are used beyond what's visible in the default recipes
- The metadata-only dependency strategy testing purpose suggests this is a simplified example - production usage may require additional configuration not present in these basic recipes
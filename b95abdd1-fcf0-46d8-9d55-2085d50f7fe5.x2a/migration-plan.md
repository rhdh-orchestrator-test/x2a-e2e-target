# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching infrastructure. The migration is relatively straightforward due to the simple nature of the cookbooks, with an estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content serving and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, basic HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services with automatic startup
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on cache and nginx cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local)**: Convert to Ansible role dependency in requirements.yml or include as part of the same playbook

### Security Considerations

- **File permissions**: The cookbook creates files with explicit mode '0644' and ownership (root:root) - ensure Ansible file module maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **Web content security**: Static HTML content is created with specific ownership - maintain proper file security in Ansible templates
- **No secrets management**: No encrypted data bags, vault usage, or credential patterns detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared but not managed by Berksfile/Policyfile - will need to be handled through Ansible Galaxy or package management
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with proper defaults
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache role, external nginx dependency)

### Assumptions

- The external nginx dependency mentioned in metadata.rb will be satisfied through system package management rather than a separate cookbook/role
- The target environment has internet access for package installation via apt/yum
- The current Chef setup uses default package repositories and doesn't require custom nginx builds or configurations
- The metadata-only dependency strategy testing purpose suggests this is a development/testing environment rather than production
- No custom nginx configuration files are required beyond the basic service setup shown in the recipes
- The simple HTML content creation is sufficient and doesn't require dynamic templating
- Redis configuration uses distribution defaults and doesn't require custom redis.conf modifications
- Platform support will be maintained for Ubuntu 18.04+ and CentOS 7.0+ as specified in the original metadata
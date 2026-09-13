# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with moderate complexity due to external dependencies and service management requirements. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role dependency in requirements.yml

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode '0644' and root ownership - maintain in Ansible file module
- **Service management**: Both nginx and redis services require proper startup and enablement - use ansible.builtin.service module
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible Galaxy role or create custom nginx role
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with proper defaults
- **Service ordering**: Ensure proper dependency ordering between nginx installation and configuration file deployment

### Migration Order

1. **cache** (low risk, simple Redis installation with no external dependencies)
2. **simple-nginx** (moderate complexity, depends on cache role and external nginx configuration)

### Assumptions

- The external 'nginx' cookbook dependency will be replaced with a suitable Ansible Galaxy role or custom role implementation
- Target systems have package managers compatible with the specified OS versions (apt for Ubuntu, yum/dnf for CentOS)
- Redis and nginx packages are available in the target system repositories
- The metadata-only dependency strategy testing purpose suggests this is a development/testing environment rather than production
- No complex nginx configuration beyond basic service setup is required based on the simple recipe content
- The '/var/www/html' directory structure is appropriate for the target nginx installation
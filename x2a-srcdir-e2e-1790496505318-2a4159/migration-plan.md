# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on web server and caching service provisioning. The scope is relatively small but demonstrates key Chef-to-Ansible migration patterns including local dependencies, package management, and service configuration.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic HTML content deployment and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: nginx package installation, service enablement, custom index.html deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: redis-server package installation, service management, basic Redis configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules or custom role
- **cache (local)**: Convert to Ansible role with Redis installation and configuration tasks
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for index.html - ensure Ansible tasks maintain proper file security
- **Service user configuration**: nginx user configuration via attributes needs proper mapping to Ansible variables
- **No secrets management**: No encrypted data bags, vault usage, or credential patterns detected in the reviewed files
- **Basic security posture**: Standard package installation without additional hardening configurations

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify appropriate Ansible Galaxy role or create custom nginx role
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with proper defaults
- **Service dependency ordering**: Ensure proper task ordering for package installation before service management
- **Cross-platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Convert Redis package installation and service management
   - Simple role with minimal complexity
2. **simple-nginx cookbook** (moderate complexity due to external dependency)
   - Resolve nginx external dependency strategy
   - Convert package installation, service management, and file deployment
   - Integrate with converted cache role

### Assumptions

- The external 'nginx' dependency will need to be resolved through Ansible Galaxy community roles or custom role development since no Berksfile/Policyfile exists for dependency resolution
- Target systems have standard package managers (apt for Ubuntu, yum/dnf for CentOS) available
- The metadata-only dependency strategy mentioned in README suggests this is a test/example cookbook, so production hardening requirements may be minimal
- No complex configuration templates or advanced nginx features are required beyond basic installation and service management
- Redis configuration can remain at default settings since no custom configuration files are present in the cache cookbook
- The cookbook's purpose as a "testing" cookbook suggests migration complexity should remain minimal to preserve the original simple design intent
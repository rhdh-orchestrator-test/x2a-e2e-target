# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution for the external nginx cookbook.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on cache (local) and nginx (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules or nginx role from Ansible Galaxy
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Package installation**: No version pinning observed - consider adding version constraints in Ansible for reproducibility
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible nginx role or create custom tasks
- **Attribute translation**: Chef attributes (nginx port, user, worker_processes) need conversion to Ansible variables with proper precedence
- **Service ordering**: Ensure proper task ordering between package installation and service management in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers (apt vs yum/dnf)

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Migrate Redis installation and service management to standalone Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Migrate nginx installation, configuration, and static content deployment after resolving external nginx dependency

### Assumptions

- The external nginx dependency can be replaced with community Ansible roles or custom tasks since no Berksfile/Policyfile exists to define the specific nginx cookbook version
- The target environment will have internet access for package installation via apt/yum repositories
- The metadata-only dependency strategy indicates this is a test/example cookbook, so production hardening requirements may be minimal
- No custom nginx configuration files are required beyond the basic service setup and static HTML content
- Redis configuration can remain at defaults since no custom configuration is specified in the cache cookbook
- The Chef version requirement (>= 16.0) suggests relatively modern infrastructure that should be compatible with current Ansible versions
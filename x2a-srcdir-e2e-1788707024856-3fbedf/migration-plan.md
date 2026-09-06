# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both a main cookbook and a local dependency, making it an excellent candidate for establishing migration patterns and testing Ansible conversion workflows.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 1-2 weeks
**Team Coordination**: Minimal (2 cookbooks, straightforward dependencies)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **simple-nginx**:
    - Description: Simple nginx web server cookbook with basic configuration, service management, and custom index page creation
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service management (enable/start), static file creation, attribute-driven configuration for port, user, and worker processes

- **cache**:
    - Description: Redis cache server cookbook providing caching services as a local dependency
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server package installation, service management (enable/start), basic cache infrastructure

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external) cookbooks, platform support for Ubuntu 18.04+ and CentOS 7+
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port (80), user (www-data), and worker processes (auto)
- `README.md`: Documentation explaining metadata-only dependency strategy for X2A Convertor testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address
- **cache (local cookbook)**: Convert to Ansible role or include tasks directly in main playbook
- **nginx (external dependency)**: Replace with community.general.nginx or geerlingguy.nginx Ansible role from Ansible Galaxy
- **Chef >= 16.0**: Remove Chef-specific version constraints, ensure Ansible 2.9+ compatibility

### Security Considerations
- **File permissions**: The cookbook creates `/var/www/html/index.html` with mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module provides equivalent security through proper systemd integration
- **Package installation**: No version pinning detected - consider adding version constraints in Ansible for security and reproducibility
- **Vault/secrets management**: 
  - **simple-nginx**: No credentials detected - uses default configurations only
  - **cache**: No credentials detected - uses default Redis configuration without authentication
  - **Total credential count**: 0 hardcoded credentials found across both modules

### Technical Challenges
- **Dependency resolution**: The external 'nginx' dependency is declared but not fetchable without Berks/Policy - need to identify appropriate Ansible Galaxy role or create custom nginx tasks
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with proper defaults
- **Service ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and configuration sequence
- **Platform compatibility**: Maintain support for both Ubuntu (apt) and CentOS (yum/dnf) package managers in Ansible tasks

### Migration Order
1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, depends on cache, requires external nginx dependency resolution)

### Assumptions
- The external 'nginx' dependency mentioned in metadata.rb is not present in the repository and will need to be sourced from Ansible Galaxy or implemented as custom tasks
- The cookbook is designed for testing metadata-only dependency strategies, suggesting this may be part of a larger Chef-to-Ansible conversion tooling project
- Default Redis configuration without authentication is acceptable for the target environment
- The simple index.html file content can be maintained as-is in the Ansible conversion
- Platform support should be maintained for both Ubuntu and CentOS families
- No custom Chef resources or complex Ruby logic is present, making conversion straightforward
- The cookbook structure suggests this is a reference implementation rather than production code, but migration should maintain full functionality
- No encrypted data bags, Chef Vault, or other Chef-specific secret management is in use
- Service management through systemd is available on target platforms
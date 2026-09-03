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
    - Description: Simple nginx web server cookbook with basic installation, service management, and static content deployment
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, static HTML file creation, attribute-driven configuration

- **cache**:
    - Description: Redis cache server cookbook providing caching services as a local dependency
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management, basic cache functionality

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `recipes/default.rb`: Main nginx installation and configuration recipe
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management recipe
- `README.md`: Documentation explaining metadata-only dependency strategy for testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced Redis management
- **cache (local cookbook)**: Convert to Ansible role and establish proper role dependency structure

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with mode 0644 and root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **No secrets detected**: This is a test cookbook with no hardcoded credentials, encrypted data bags, or vault usage
- **Static content**: HTML content is hardcoded in recipe - consider templating approach in Ansible for better maintainability

### Technical Challenges

- **Dependency resolution**: The cookbook depends on an external 'nginx' cookbook that is "declared but not fetchable without Berks/Policy" - need to identify and replace this external dependency with appropriate Ansible modules or roles
- **Attribute mapping**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need to be converted to Ansible variables with proper defaults and variable precedence
- **Platform support**: Cookbook supports both Ubuntu and CentOS - ensure Ansible playbooks handle package name differences and service management variations between distributions
- **Testing strategy**: Original cookbook appears designed for testing metadata-only dependency strategy - migration testing approach needs to be established

### Migration Order

1. **cache cookbook** (Priority 1: Simple, no external dependencies, provides foundation for testing dependency patterns)
2. **simple-nginx cookbook** (Priority 2: Depends on cache, includes external nginx dependency resolution)

### Assumptions

- The external 'nginx' cookbook dependency mentioned in metadata.rb will need to be replaced with community Ansible roles or custom role development
- Target environments will have package managers available (apt for Ubuntu, yum/dnf for CentOS)
- The migration is intended to maintain the same testing purpose (metadata-only dependency strategy validation)
- No complex configuration management or templating is required beyond the basic static HTML file
- Service management follows standard systemd patterns on target platforms
- The cookbook's testing nature suggests this migration may serve as a template for larger, more complex cookbook migrations
- No integration with Chef Server, encrypted data bags, or Chef Vault is present
- The simple nature of the cookbooks suggests they may be part of a larger migration testing framework
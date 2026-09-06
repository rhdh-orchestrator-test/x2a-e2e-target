# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting 2 Chef cookbooks (simple-nginx and cache) to Ansible roles. This is a low-complexity migration with an estimated timeline of 1-2 weeks for a single developer, suitable as a proof-of-concept for larger Chef-to-Ansible migrations.

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
- Key Features: Redis package installation, service management, basic cache functionality

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port 80, www-data user, auto worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for X2A Convertor testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis installation and service management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with mode 0644 and root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **No secrets detected**: This repository contains no encrypted data bags, vault usage, or hardcoded credentials

### Technical Challenges

- **External nginx dependency**: The main cookbook depends on an external 'nginx' cookbook that is declared but not present in the repository - migration will need to implement nginx configuration directly or identify the appropriate Ansible nginx role
- **Metadata-only strategy**: The repository is designed for testing metadata-only dependency resolution, which may not translate directly to Ansible's role dependency model
- **Platform support**: Cookbook supports both Ubuntu and CentOS - Ansible playbooks will need conditional logic for package manager differences (apt vs yum)

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Convert redis package installation to ansible.builtin.package
   - Convert service management to ansible.builtin.service
   - Create role structure with tasks/main.yml, handlers/main.yml, meta/main.yml

2. **simple-nginx cookbook** (moderate complexity, external dependency)
   - Resolve external nginx dependency strategy
   - Convert package installation and service management
   - Migrate file creation for custom index.html
   - Convert attributes to Ansible variables in defaults/main.yml
   - Update dependency references to use Ansible role dependencies

### Assumptions

- The external 'nginx' cookbook dependency will need to be resolved through community Ansible roles or custom implementation since it's not present in the source repository
- Target systems will have appropriate package managers (apt for Ubuntu, yum/dnf for CentOS) configured and accessible
- The metadata-only dependency strategy mentioned in the README is specific to the X2A Convertor tool and may not require direct migration to Ansible
- No custom Chef resources or complex cookbook patterns are present that would require advanced Ansible module development
- The simple nature of these cookbooks suggests they are primarily for testing rather than production use, allowing for straightforward role-based migration
- Platform support declarations in Chef metadata.rb will be migrated to Ansible meta/main.yml with appropriate platform specifications
- Service user configurations (www-data) are assumed to exist on target systems or will be created as part of package installation
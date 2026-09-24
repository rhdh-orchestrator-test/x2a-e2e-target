# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that provide basic web server and caching functionality. The migration is relatively straightforward due to the simple nature of the cookbooks, minimal dependencies, and clear separation of concerns. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic Nginx web server installation and configuration with custom index page and configurable attributes
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration for port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker_processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on metadata.rb platform support declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified in source configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate to Ansible tasks using ansible.builtin.package and ansible.builtin.service for Redis installation

### Security Considerations

- **File permissions**: Static HTML file creation uses explicit mode '0644' and ownership (root:root) - ensure Ansible file module maintains same security posture
- **Service management**: Both cookbooks manage system services (nginx, redis-server) - verify proper systemd integration in target environment
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, external dependency resolution needed, attribute system conversion required)

### Assumptions

- The external 'nginx' dependency refers to a standard community nginx cookbook with basic installation and configuration capabilities
- Target systems have package managers compatible with 'nginx' and 'redis-server' package names (apt for Ubuntu, yum/dnf for CentOS)
- No custom nginx configuration templates are required beyond the basic installation (none found in the repository)
- The metadata-only dependency strategy indicates this is a test/example repository rather than a production cookbook with complex requirements
- Chef version '>= 16.0' requirement suggests modern Chef practices that should translate well to current Ansible versions
- Platform support for Ubuntu 18.04+ and CentOS 7+ indicates standard Linux package management expectations
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution for the external nginx cookbook.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level)
- Technology: Chef
- Key Features: Package installation, service enablement, static file creation, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules or nginx role from Ansible Galaxy
- **cache (local)**: Migrate directly as it's a simple Redis installation cookbook

### Security Considerations

- **Package Management**: Both cookbooks use simple package installation without version pinning - consider implementing version constraints in Ansible
- **Service Security**: No advanced security configurations detected - basic service management only
- **File Permissions**: Static file creation uses standard permissions (0644, root:root) - maintain same security posture in Ansible
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External Dependency Resolution**: The nginx external dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify appropriate Ansible nginx role or create custom tasks
- **Attribute Translation**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Service Management**: Chef service resources need mapping to ansible.builtin.systemd or ansible.builtin.service modules
- **Platform Support**: Ensure Ansible playbooks maintain the same Ubuntu/CentOS support matrix

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and attribute configuration)

### Assumptions

- The external nginx dependency referenced in metadata.rb will be replaced with a suitable Ansible role from Galaxy or custom implementation
- Target systems have package managers available (apt for Ubuntu, yum/dnf for CentOS)
- No complex Chef-specific features (encrypted data bags, search, etc.) are used beyond what's visible in the reviewed files
- The metadata-only strategy indicates this is a test/example repository rather than production infrastructure
- Service management assumes systemd is available on target platforms
- No custom Chef resources or libraries are in use beyond standard Chef resources
- File paths and permissions requirements remain the same across Chef and Ansible implementations
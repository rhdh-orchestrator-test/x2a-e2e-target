# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. The estimated timeline is 1-2 weeks for a small team, with low to moderate complexity due to the straightforward nature of the cookbooks and minimal external dependencies.

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

- `metadata.rb`: Root cookbook metadata with external nginx dependency and local cache dependency
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules or nginx role from Ansible Galaxy
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Use ansible.builtin.package for installation and ansible.builtin.service for management

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 and root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **Package installation**: No version pinning observed - consider implementing version constraints in Ansible for reproducible deployments
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not resolved through Berksfile or Policyfile - will need to identify the specific nginx cookbook requirements and translate to appropriate Ansible nginx role or modules
- **Attribute translation**: Chef attributes in `attributes/default.rb` need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same deployment sequence as Chef run_list
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in cookbook metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external nginx dependency refers to a standard community nginx cookbook that can be replaced with community Ansible nginx roles
- The target environments have package managers (apt/yum) available for nginx and redis installation
- No custom nginx configuration templates are required beyond the basic setup shown
- The metadata-only dependency strategy indicates this is a test/example repository rather than production code
- No encrypted secrets or vault integration is required based on the simple nature of the cookbooks
- The cookbook supports both Ubuntu and CentOS but specific version requirements may need validation during migration
- No complex nginx virtual host configurations are needed beyond the simple index.html file creation
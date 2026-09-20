# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, configurable attributes for port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules or nginx role from Ansible Galaxy
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for the index.html file - ensure Ansible playbooks maintain proper file ownership and permissions
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible equivalents
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **User management**: Nginx user configuration (www-data) needs to be handled appropriately in Ansible

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile or Policyfile - need to identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes system needs to be converted to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to handle service dependencies
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple Redis setup)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and attribute system)

### Assumptions

- The external 'nginx' dependency refers to a standard community nginx cookbook with basic installation and configuration capabilities
- The target environment will have package managers (apt/yum) available for nginx and redis installation
- No custom nginx configuration beyond basic setup is required (only simple index page replacement)
- Redis configuration can use default settings as no custom configuration is specified in the cache cookbook
- The metadata-only strategy mentioned in documentation suggests this is a test/example repository rather than production code
- Platform support requirements (Ubuntu 18.04+, CentOS 7.0+) should be maintained in the Ansible migration
- No complex Chef-specific features (encrypted data bags, custom resources, etc.) are in use based on the simple recipe structure observed
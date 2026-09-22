# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two modules that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that require careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root level cookbook)
    - Technology: Chef
    - Key Features: Package installation, service management, static file deployment, attribute-driven configuration

- **cache**:
    - Description: Redis cache server installation and service management for local dependency testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package module and redis configuration via ansible.builtin.template if needed

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 and root ownership - ensure Ansible playbook maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible
- **No secrets management**: No encrypted data bags, vault usage, or credential patterns detected in the reviewed files
- **Default configurations**: Using default nginx and redis configurations - review for production security hardening needs

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - need to identify the specific nginx cookbook version and features required
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks for service dependencies
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in original metadata

### Migration Order

1. **cache module** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx module** (moderate complexity, depends on cache module, external nginx dependency to resolve)

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook from Chef Supermarket - specific version and features need identification
- Current deployment uses default nginx and redis configurations suitable for development/testing
- No custom templates, files, or complex configurations beyond what's visible in the default recipes
- The metadata-only strategy suggests this is a test/example cookbook rather than production infrastructure
- Platform support requirements (Ubuntu 18.04+, CentOS 7.0+) should be maintained in Ansible playbooks
- No encrypted data bags or Chef Vault usage based on the simple cookbook structure
- Service management follows standard systemd patterns on supported platforms
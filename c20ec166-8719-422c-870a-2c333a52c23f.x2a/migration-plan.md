# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with explicit mode 0644 and root ownership - ensure Ansible playbook maintains these security settings
- **Service management**: Both nginx and redis services are enabled and started - verify service security configurations in Ansible equivalents
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files - this is a low-risk migration from a secrets perspective

### Technical Challenges

- **External dependency resolution**: The cookbook depends on an external 'nginx' cookbook that is declared but not fetchable without Berksfile or Policyfile - this dependency needs to be resolved or replaced with direct Ansible nginx configuration
- **Attribute translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables with appropriate scoping
- **Service ordering**: Ensure proper dependency ordering between package installation and service management in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in the original cookbook metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external 'nginx' cookbook dependency will need to be replaced with direct Ansible nginx configuration since no Berksfile or Policyfile exists to resolve it
- The target environment has internet access for package installation via apt/yum
- The migration will maintain the same platform support (Ubuntu 18.04+, CentOS 7.0+) as specified in the original cookbook metadata
- No custom nginx configuration files are required beyond the basic installation and simple index page
- Redis will use default configuration since no custom configuration is specified in the cache cookbook
- The metadata-only dependency strategy mentioned in the README suggests this is a test/example repository rather than production code
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small with basic web server and caching functionality, making this a low-complexity migration suitable for completion within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in configuration files
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain proper startup behavior
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files - this is a clean migration from a security perspective

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata.rb but no Berksfile or Policyfile exists, suggesting this cookbook relies on external dependency management - Ansible migration will need to handle nginx installation directly
- **Attribute translation**: Chef attributes in attributes/default.rb need conversion to Ansible variables with appropriate precedence handling
- **Service ordering**: Ensure proper dependency ordering between nginx and cache services in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The nginx external dependency mentioned in metadata.rb refers to the standard nginx web server package available in OS repositories, not a specific Chef community cookbook
- The target environment has internet access for package installation from standard repositories
- The current deployment uses the default nginx configuration with minimal customization beyond the attributes specified
- No complex nginx virtual host configurations or SSL/TLS certificates are required based on the simple nature of the cookbook
- The redis installation uses default configuration without clustering or advanced caching features
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ as explicitly declared in cookbook metadata
- No Chef Server integration or encrypted data bag dependencies exist since none were found in the repository structure
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook demonstration with nginx web server and Redis cache components. The migration scope is relatively straightforward with two cookbooks and minimal external dependencies. Estimated timeline: 1-2 weeks for a small team, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with nginx external dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate Redis installation to ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - maintain same security posture in Ansible
- **Service management**: Both nginx and Redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Network security**: Default nginx configuration exposes port 80 - consider firewall rules and SSL/TLS configuration in Ansible implementation

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile - will need to identify appropriate Ansible Galaxy role or implement custom nginx configuration
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need to be converted to Ansible variables with appropriate defaults
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Simple Redis installation with package and service management
2. **simple-nginx cookbook** (moderate complexity) - Nginx installation with custom configuration and static content deployment

### Assumptions

- The nginx external dependency refers to a standard nginx installation rather than a complex community cookbook with advanced features
- The current setup is intended for development/testing environments given the simple configuration and static HTML content
- No complex nginx virtual host configurations, SSL certificates, or reverse proxy setups are required based on the minimal recipe content
- Redis configuration uses default settings since no custom configuration files or templates were found in the cache cookbook
- The metadata-only dependency strategy mentioned in README suggests this is a testing/demonstration repository rather than production infrastructure
- Platform support is limited to Ubuntu and CentOS as explicitly declared in metadata, though Ansible implementation could potentially support additional distributions
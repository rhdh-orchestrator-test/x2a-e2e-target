# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef-based infrastructure setup with nginx web server and Redis caching components. The migration involves converting 2 Chef cookbooks to Ansible roles, with minimal complexity due to the straightforward nature of the configurations. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic nginx web server installation with service management and simple static content deployment
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file creation, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy and cookbook purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be cloud-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role with redis package management and service configuration

### Security Considerations

- **File permissions**: Static HTML file created with explicit 0644 permissions and root ownership - maintain same security posture in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files
- **SSL/TLS certificates**: No certificate management found in current configuration

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile - will need to identify appropriate Ansible Galaxy role or create custom nginx configuration
- **Attribute translation**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx setup with external dependency resolution and attribute handling

### Assumptions

- The external nginx dependency referenced in metadata.rb will need to be resolved through Ansible Galaxy community roles or custom implementation
- Current configuration is intended for development/testing environments based on the simple static content and lack of advanced security configurations
- No complex template rendering or dynamic configuration generation is required based on the static HTML file creation
- The metadata-only dependency strategy mentioned in documentation suggests this is a test/example repository rather than production infrastructure
- No encrypted secrets or sensitive data management is currently implemented
- Service configurations use default settings without custom configuration files or advanced tuning parameters
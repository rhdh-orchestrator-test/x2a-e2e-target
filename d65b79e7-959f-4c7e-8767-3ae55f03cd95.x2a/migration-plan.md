# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup with nginx web server and redis cache components. The migration involves converting 2 cookbooks with minimal complexity, making this a straightforward migration suitable for completion within 1-2 weeks by a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Nginx web server installation and basic configuration with custom index page and service management
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, basic nginx configuration via attributes

**cache**:
- Description: Redis server installation and service management for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes) - will need conversion to Ansible variables
- `README.md`: Documentation explaining metadata-only dependency strategy - should be updated for Ansible approach

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert internal dependency to Ansible role or include within main playbook

### Security Considerations

- **File permissions**: Static file creation uses explicit mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files - this is a low-risk migration from a secrets perspective

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external 'nginx' dependency without Berksfile/Policyfile - migration team will need to identify appropriate Ansible Galaxy roles or create custom nginx configuration
- **Attribute translation**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Service ordering**: Ensure proper dependency ordering between nginx and cache services in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert redis installation and service management to Ansible tasks
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and static content deployment, resolve external nginx dependency

### Assumptions

- The external 'nginx' dependency mentioned in metadata.rb is assumed to provide additional nginx configuration beyond basic package installation - migration team will need to research what specific nginx functionality this dependency provides
- Target systems will have package managers (apt/yum) available as assumed by Chef package resources
- The cookbook is designed for testing purposes (as indicated in README) - production deployment may require additional hardening and configuration not present in these simple recipes
- No custom templates, files, or complex configuration management detected - actual production usage may require additional Ansible components not evident from this test cookbook structure
- Service management assumes systemd or compatible init system based on the service resource usage patterns
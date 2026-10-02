# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef-based infrastructure setup with two cookbooks focused on web server and caching functionality. The migration involves converting basic package installation, service management, and file deployment patterns to Ansible equivalents. Estimated timeline: 1-2 weeks for a small team, with low complexity due to straightforward resource types and minimal dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Basic Nginx web server installation with service management and simple HTML content deployment
- Path: . (root level cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement/startup, static file creation with ownership/permissions

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management and auto-start configuration

### Infrastructure Files

- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes) - will need conversion to Ansible variables
- `README.md`: Documentation describing metadata-only dependency strategy - update for Ansible approach

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Convert to Ansible role with redis installation and configuration tasks

### Security Considerations

- File permissions: Current implementation uses explicit mode '0644', owner 'root', group 'root' - maintain same security posture in Ansible
- Service management: Both cookbooks enable and start services - ensure Ansible playbooks maintain same security practices
- Vault/secrets management: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files
- No SSL/TLS certificate management or environment variable secrets identified

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile/Policyfile - will need to identify appropriate Ansible Galaxy role or create custom tasks
- **Multi-platform support**: Cookbooks support both Ubuntu and CentOS - Ansible playbooks will need conditional logic for package manager differences (apt vs yum/dnf)
- **Service naming variations**: Redis service name may differ between platforms (redis-server vs redis) - requires platform-specific handling

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple package + service pattern)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency and file management)

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb will need to be resolved through Ansible Galaxy roles or custom task implementation
- Current attribute-based configuration (nginx port, user, worker processes) suggests need for templated nginx.conf management not visible in the basic recipe
- No complex template rendering or data bag usage detected, but full nginx configuration may require additional investigation
- Service names and package names are assumed to be consistent with standard distributions - may need verification for target environments
- No custom resources, libraries, or complex Chef-specific patterns identified that would complicate migration
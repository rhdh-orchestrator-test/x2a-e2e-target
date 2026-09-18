# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that provide basic web server and caching functionality. The migration scope is relatively small but demonstrates key Chef patterns including local dependencies and external cookbook references. Estimated migration timeline: 1-2 weeks for a small team, with low to moderate complexity due to the straightforward service management patterns.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation and configuration with basic service management and static content deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static HTML file creation, configurable nginx attributes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
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
- **cache (local)**: Migrate Redis installation and service management to Ansible using ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file creation uses explicit mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain proper startup behavior
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared in metadata but not resolved via Berksfile or Policyfile - need to identify what nginx configurations this external dependency provides
- **Attribute-driven configuration**: The nginx attributes (port, user, worker_processes) need to be converted to Ansible variables with appropriate defaults
- **Service ordering**: Ensure proper dependency ordering between nginx and cache services in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Migrate Redis installation and service management first
2. **simple-nginx cookbook** (moderate complexity) - Migrate nginx installation, service management, and static content after resolving external nginx cookbook dependency requirements

### Assumptions

- The external 'nginx' cookbook dependency provides standard nginx installation and configuration - actual functionality unknown without access to the external cookbook source
- Target systems will have package managers (apt/yum) available for nginx and redis-server packages
- Current Chef run_list and node attributes are not visible in this repository - migration will need to account for how these cookbooks are currently applied
- No custom templates, files, or complex configuration management beyond basic service setup
- The metadata-only dependency strategy mentioned in README suggests this is a test/example repository rather than production infrastructure
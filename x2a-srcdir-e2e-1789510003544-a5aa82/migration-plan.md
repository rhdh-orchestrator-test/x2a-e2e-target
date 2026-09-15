# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root level cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, static file deployment, configurable port and worker processes

- **cache**:
    - Description: Redis server installation and configuration for caching services
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis-server package installation, service management, basic cache functionality

### Infrastructure Files

- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes) - will need conversion to Ansible variables
- `README.md`: Documentation explaining metadata-only dependency strategy - should be updated for Ansible approach

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Convert to Ansible role or include in main playbook as tasks

### Security Considerations

- **File permissions**: Static file creation uses explicit mode '0644', owner 'root', group 'root' - ensure Ansible file module maintains same security posture
- **Service security**: Both nginx and redis services are enabled and started - verify default configurations meet security requirements
- **Vault/secrets management**: No encrypted data bags, vault usage, or hardcoded credentials detected in the reviewed files - migration should maintain this clean security posture

### Technical Challenges

- **Metadata-only dependency strategy**: The cookbook declares an external 'nginx' dependency in metadata.rb but doesn't use a Berksfile or Policyfile for resolution - need to identify the actual nginx cookbook source or replace with Ansible nginx role
- **Local dependency structure**: The cache cookbook is embedded locally - decision needed whether to convert to separate Ansible role or integrate into main playbook
- **Attribute inheritance**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Cross-platform support**: Both Ubuntu and CentOS support declared - ensure Ansible playbooks handle package name differences (nginx vs nginx, redis-server vs redis)

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity due to external nginx dependency and attribute system)

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb is a standard nginx cookbook - actual source and version need identification
- Target environments will have the same OS support requirements (Ubuntu 18.04+, CentOS 7+)
- Redis and nginx packages are available in target environment repositories
- No custom nginx configuration beyond basic attributes is required
- The metadata-only strategy indicates this is a test/example repository rather than production code
- No encrypted secrets or sensitive data are present in the configuration
- Default service configurations for nginx and redis are acceptable for the target environment
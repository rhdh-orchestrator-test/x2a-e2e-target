# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef-based infrastructure setup with two cookbooks focused on web server and caching functionality. The migration scope is relatively small but demonstrates a metadata-only dependency strategy that will require careful handling during the Ansible conversion. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being external dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **cache (local)**: Migrate to dedicated Ansible role for Redis installation and configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file uses explicit 0644 permissions and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **Vault/secrets management**: No encrypted data bags, Chef Vault, or hardcoded credentials detected in the reviewed files
- **Package sources**: Default package repositories used - consider pinning package versions in Ansible for security consistency

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata.rb but not managed by Berksfile or Policyfile, requiring manual resolution of the nginx cookbook functionality during migration
- **Metadata-only strategy**: The current setup relies on metadata declarations without explicit dependency management tools, which may indicate missing configuration that needs to be discovered and implemented in Ansible
- **Service ordering**: Ensure proper dependency ordering between nginx and cache services in Ansible playbooks
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package naming differences (redis-server vs redis)

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Migrate Redis installation and service management to standalone Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Migrate nginx installation, configuration, and static content deployment, resolving external nginx dependency requirements
3. **Integration testing** (high complexity) - Validate cross-cookbook functionality and service interactions in target environments

### Assumptions

- The external nginx dependency contains standard nginx cookbook functionality that can be replaced with community Ansible modules
- No custom nginx configuration templates are required beyond the basic setup shown in the recipes
- Redis configuration uses default settings and doesn't require custom configuration files
- The metadata-only dependency strategy doesn't hide additional configuration requirements not visible in the current repository
- Target environments have standard package repositories available for nginx and redis installation
- No additional Chef environments, roles, or data bags exist outside this repository that affect these cookbooks
- The simple HTML content deployment pattern is sufficient and doesn't require dynamic content generation
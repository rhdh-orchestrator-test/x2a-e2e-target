# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **cache (local)**: Migrate redis installation to ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 with root ownership - maintain same security posture in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management
- **Package sources**: No custom repositories specified - uses default system package managers
- **Secrets management**: No credentials or sensitive data identified in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile, requiring manual resolution of the actual nginx cookbook requirements
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper startup order between nginx and cache services if they interact
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS with appropriate package name variations

### Migration Order

1. **cache cookbook** (low risk, no external dependencies, simple redis installation)
2. **simple-nginx cookbook** (moderate complexity, external dependency, file management)

### Assumptions

- The external nginx dependency referenced in metadata.rb is assumed to be the standard community nginx cookbook, but this needs verification since no Berksfile or Policyfile exists to specify the source
- The cookbooks are designed to run independently without complex inter-cookbook communication
- Default system package repositories contain the required nginx and redis packages
- The target environment will use the same package names across Ubuntu and CentOS (may require conditional logic for package name variations)
- No custom nginx configuration beyond the basic attributes is required
- The static HTML file content can be migrated as-is without dynamic templating needs
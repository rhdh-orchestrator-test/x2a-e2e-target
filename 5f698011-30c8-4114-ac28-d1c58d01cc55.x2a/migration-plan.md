# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration involves converting basic web server and caching service configurations to Ansible playbooks. This is a low-complexity migration with an estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML file deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Internal dependency that will be converted to Ansible role or included tasks

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 with root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module configurations maintain security best practices
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared in metadata but not managed by Berksfile or Policyfile - migration will need to handle this dependency explicitly in Ansible requirements
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service ordering**: Ensure proper dependency ordering between nginx installation and configuration in Ansible playbooks

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Simple Redis installation and service management
   - Good candidate for initial migration validation

2. **simple-nginx cookbook** (moderate complexity)
   - Depends on cache cookbook completion
   - Requires handling of external nginx dependency
   - File creation and service management

### Assumptions

- The external nginx dependency will be resolved through standard package managers rather than requiring a separate Ansible role
- The target environment has internet access for package installation
- The metadata-only dependency strategy indicates this is a test/example cookbook rather than production infrastructure
- No complex nginx configuration beyond basic service setup is required based on the simple recipe content
- Redis configuration uses default settings since no custom configuration files are present in the cache cookbook
- The cookbook supports both Ubuntu and CentOS, but the migration may initially target a single OS family for simplicity
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks demonstrating a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies that need careful handling. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
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

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **Metadata-only dependency strategy**: The repository uses metadata.rb declarations without Berksfile or Policyfile, requiring manual dependency resolution during migration
- **External nginx dependency**: The nginx dependency is declared but not fetchable without proper dependency management tools, requiring identification of the specific nginx cookbook version and features needed
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper scoping and precedence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
2. **simple-nginx cookbook** (moderate complexity due to external nginx dependency)

### Assumptions

- The external nginx dependency refers to the community nginx cookbook, though the specific version and required features are not specified
- The target environment will have package managers available (apt for Ubuntu, yum/dnf for CentOS)
- The metadata-only strategy suggests this is a testing or demonstration environment rather than production
- No custom templates, files, or complex configurations exist beyond what's visible in the default recipes
- The nginx dependency may require additional research to identify the specific cookbook version and features being used
- Platform support is limited to Ubuntu 18.04+ and CentOS 7.0+ as explicitly declared in metadata files
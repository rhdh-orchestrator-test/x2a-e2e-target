# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two cookbooks (one main cookbook and one local dependency) that provide basic web server and caching functionality. The scope is relatively small but demonstrates key Chef patterns that need translation to Ansible. Estimated timeline: 1-2 weeks for a single developer, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis server installation and configuration for caching functionality
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service enablement and startup

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx Ansible Galaxy collection for advanced configuration
- **cache (local)**: Convert to Ansible role with redis installation and configuration tasks
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for the index.html file - ensure Ansible file module maintains proper permissions
- **Service user configuration**: Nginx user configuration via attributes needs to be translated to Ansible variables
- **No secrets management**: No encrypted data bags, vault usage, or credential management detected in the current implementation

### Technical Challenges

- **Metadata-only dependency strategy**: The repository is designed to test dependency resolution without Berksfile or Policyfile - migration needs to handle the external 'nginx' dependency that may not be locally available
- **Attribute translation**: Chef attributes (nginx port, user, worker processes) need conversion to Ansible variables with appropriate defaults
- **Service management**: Both cookbooks use Chef service resources that need translation to Ansible service module with proper state management

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and file management, handle external nginx dependency resolution

### Assumptions

- The external 'nginx' dependency referenced in metadata.rb is assumed to be the standard nginx cookbook from Chef Supermarket - migration will need to identify and replace this with appropriate Ansible Galaxy nginx role or custom tasks
- Platform support is limited to Ubuntu 18.04+ and CentOS 7.0+ as specified in metadata - Ansible playbooks should target these OS families
- The cookbook is designed for testing purposes (metadata-only strategy) - production migration may require additional configuration and hardening
- No complex templating or advanced Chef features are used - migration should be straightforward with basic Ansible modules
- Service management assumes systemd on target platforms based on supported OS versions
- No custom Chef resources or libraries are present that would require complex Ansible module development
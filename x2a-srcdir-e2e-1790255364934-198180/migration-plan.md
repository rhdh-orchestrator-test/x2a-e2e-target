# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with a focus on maintaining the dependency relationship and basic web server functionality. Estimated timeline: 1-2 weeks for a small team, given the straightforward nature of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration, custom index page, and service management
    - Path: . (root cookbook)
    - Technology: Chef
    - Key Features: Package installation, service enablement, custom HTML content, attribute-driven configuration

- **cache**:
    - Description: Redis server installation and configuration for caching functionality
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management, basic cache server setup

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration and platform support definitions
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support for Ubuntu 18.04+ and CentOS 7+
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and nginx Ansible Galaxy role or custom tasks
- **redis-server**: Replace with ansible.builtin.package and redis configuration tasks
- **cache (internal)**: Convert to Ansible role dependency relationship

### Security Considerations
- File permissions: The cookbook creates `/var/www/html/index.html` with explicit 0644 permissions and root ownership - ensure Ansible tasks maintain proper file security
- Service management: Both nginx and redis services are enabled and started - verify proper systemd service handling in Ansible
- No vault/secrets management: No encrypted data bags, vault usage, or credential patterns detected in the reviewed files

### Technical Challenges
- **Metadata-only dependency strategy**: The root cookbook depends on an external 'nginx' cookbook that isn't present in the repository, requiring resolution of this external dependency during migration
- **Attribute translation**: Chef attributes in `attributes/default.rb` need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering when both nginx and cache services need to be managed
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package management differences

### Migration Order
1. **cache cookbook** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx cookbook** (moderate complexity, external nginx dependency, attribute handling)

### Assumptions
- The external 'nginx' dependency mentioned in metadata.rb will need to be resolved through Ansible Galaxy nginx role or custom implementation
- The target environment has internet access for package installation via apt/yum
- The cookbook is intended for testing purposes based on README documentation, so production hardening may not be required
- Default nginx configuration is acceptable since no custom nginx.conf templates are present
- Redis default configuration is sufficient as no custom redis.conf is provided
- The metadata-only strategy suggests this is part of a larger testing framework that may have additional requirements not visible in this repository
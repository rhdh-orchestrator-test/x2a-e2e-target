# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles, with moderate complexity due to external dependencies and service management requirements. Estimated timeline: 1-2 weeks for a small team.

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
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata with dependency declarations and platform support definitions
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform compatibility specifications
- `attributes/default.rb`: Nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role dependency in requirements.yml

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 - ensure Ansible file module maintains proper permissions
- **Service user**: Nginx configured to run as www-data user - verify user exists or create via Ansible
- **No secrets management**: No encrypted data bags, vault usage, or credential patterns detected in reviewed files
- **Service exposure**: Both nginx (port 80) and redis services will be exposed - consider firewall rules in Ansible playbooks

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared but not resolvable without Berksfile/Policyfile - will need to identify correct Ansible Galaxy role or create custom nginx role
- **Service ordering**: Ensure proper dependency ordering between cache (redis) and nginx services in Ansible playbooks
- **Attribute translation**: Convert Chef attributes to Ansible variables with proper precedence and scoping
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers (apt vs yum/dnf)

### Migration Order

1. **cache** (low risk, no external dependencies, simple service management)
2. **simple-nginx** (moderate complexity, depends on cache role, external nginx dependency to resolve)

### Assumptions

- The external nginx dependency mentioned in metadata.rb will need to be resolved through Ansible Galaxy or custom role development
- Target systems will have internet access for package installation
- The metadata-only dependency strategy mentioned in README suggests this is a test/example cookbook rather than production code
- No complex configuration templates or advanced nginx features are required based on the simple recipe content
- Redis configuration uses default settings since no custom configuration files were found
- The cookbook supports both Ubuntu and CentOS but actual testing may be needed to verify package name compatibility across distributions
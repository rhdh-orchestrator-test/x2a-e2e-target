# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both local and external dependencies. Estimated timeline: 1-2 weeks for a small team, with the primary complexity being dependency resolution and testing.

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

- `metadata.rb`: Main cookbook metadata with dependencies on 'cache' (local) and 'nginx' (external)
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules
- **Chef >= 16.0**: No direct equivalent needed in Ansible

### Security Considerations

- **File permissions**: Static HTML file created with explicit mode 0644, owner root:root - maintain same permissions in Ansible
- **Service management**: Both nginx and redis services are enabled and started - ensure proper service state management in Ansible
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **External dependency resolution**: The 'nginx' dependency is declared in metadata but not resolvable without Berksfile/Policyfile - will need to identify the specific nginx cookbook version and features used
- **Attribute translation**: Chef attributes need conversion to Ansible variables with proper precedence handling
- **Service dependency ordering**: Ensure proper task ordering between package installation and service management
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS as specified in metadata

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Simple redis installation and service management
   - No complex configurations or templates
   
2. **simple-nginx cookbook** (moderate complexity)
   - Depends on cache cookbook completion
   - External nginx dependency needs resolution
   - Static file management and attribute handling

### Assumptions

- The external 'nginx' dependency refers to a standard nginx cookbook with basic installation capabilities
- No custom nginx configuration templates are required beyond the simple index.html file
- The metadata-only strategy indicates this is a test/example cookbook, suggesting production complexity may be minimal
- Platform support requirements (Ubuntu 18.04+, CentOS 7.0+) will be maintained in the Ansible version
- No additional Chef environments, roles, or data bags exist outside this repository structure
- The current setup uses default nginx and redis configurations without custom tuning requirements
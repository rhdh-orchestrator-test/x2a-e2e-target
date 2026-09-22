# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook setup with two cookbooks demonstrating a metadata-only dependency strategy. The migration scope is relatively small with basic web server and caching functionality. Estimated timeline: 1-2 weeks for a single engineer, including testing and validation.

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

- `metadata.rb`: Root cookbook metadata with external nginx dependency declaration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and platform support definitions
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly supported in metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.redis.redis_* modules for advanced configuration

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode '0644' and root ownership - ensure Ansible file module maintains same security posture
- **Service management**: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- **No secrets identified**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files

### Technical Challenges

- **Metadata-only dependency strategy**: The root cookbook declares dependency on external 'nginx' cookbook but doesn't use Berksfile or Policyfile for resolution - need to identify actual nginx cookbook requirements and replace with appropriate Ansible modules
- **Platform support**: Cookbooks explicitly support both Ubuntu and CentOS - ensure Ansible playbooks handle package name differences (nginx vs nginx, redis-server vs redis)
- **Attribute-driven configuration**: Nginx attributes need conversion to Ansible variables with appropriate defaults

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Simple package installation and service management
   - No complex configuration or templates
   
2. **simple-nginx cookbook** (moderate complexity)
   - Package installation with external dependency consideration
   - Static file deployment and service management
   - Attribute-driven configuration conversion

### Assumptions

- The external 'nginx' cookbook dependency is not critical to basic functionality since the recipes only use built-in Chef resources
- Redis configuration uses default settings and doesn't require custom configuration files
- The target environment has internet access for package installation
- No custom nginx configuration beyond the basic attributes is required
- The metadata-only strategy indicates this is a test/example setup rather than production infrastructure
- Platform-specific package names (redis-server vs redis) will need to be handled in Ansible variable definitions
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

- `metadata.rb`: Main cookbook metadata with dependency declarations and platform support
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and version information
- `attributes/default.rb`: Nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role dependency in requirements.yml

### Security Considerations

- **File permissions**: Static HTML file uses explicit mode 0644 - ensure Ansible file module maintains proper permissions
- **Service user**: Nginx configured to run as www-data user - verify user exists or create in Ansible playbook
- **No secrets management**: No encrypted data bags, vault usage, or credential patterns detected in reviewed files
- **Service exposure**: Both nginx (port 80) and redis services will be exposed - consider firewall rules in Ansible implementation

### Technical Challenges

- **External dependency resolution**: The nginx external dependency is declared but not fetchable without Berksfile/Policyfile - will need to identify correct Ansible Galaxy role or create custom implementation
- **Attribute translation**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need conversion to Ansible variables with proper defaults
- **Service dependency ordering**: Ensure proper task ordering between package installation, configuration, and service startup
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers (apt vs yum)

### Migration Order

1. **cache** (low risk, no external dependencies, simple Redis installation)
2. **simple-nginx** (moderate complexity, external nginx dependency, file management)

### Assumptions

- The external nginx dependency refers to a standard nginx installation rather than a complex cookbook with advanced configurations
- The metadata-only strategy indicates this is a test/example repository rather than production code
- No custom nginx configuration files are required beyond the basic service setup
- Redis configuration can use default settings without custom redis.conf modifications
- Target environments have internet access for package installation
- The simple HTML content can be deployed as a static file without templating requirements
# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration involves converting basic web server and caching service configurations to Ansible playbooks. This is a low-complexity migration with an estimated timeline of 1-2 weeks for a single engineer.

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

- `metadata.rb`: Main cookbook metadata with dependency declarations on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx collection for advanced configuration
- **cache (local)**: Convert Redis installation and service management to Ansible redis role or custom tasks
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations

- **File permissions**: The cookbook sets explicit file permissions (0644) for the index.html file - ensure Ansible tasks maintain proper file ownership and permissions
- **Service management**: Both nginx and redis services are enabled and started - verify proper service security configurations in Ansible
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Default configurations**: Using default nginx and redis configurations - review security hardening requirements for production deployment

### Technical Challenges

- **External dependency resolution**: The 'nginx' cookbook dependency is declared in metadata but not resolvable without Berksfile or Policyfile - need to identify the specific nginx cookbook requirements and replace with appropriate Ansible nginx role
- **Attribute translation**: Convert Chef attributes (nginx port, user, worker_processes) to Ansible variables with proper precedence and scoping
- **Service dependency ordering**: Ensure proper task ordering in Ansible playbooks to match Chef's resource dependency model
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS platforms using Ansible's conditional task execution

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to standalone Ansible tasks
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and static content deployment, resolve external nginx dependency requirements

### Assumptions

- The external 'nginx' cookbook dependency provides standard nginx installation and configuration - specific requirements need to be identified from the original cookbook source or documentation
- Default nginx and redis configurations are sufficient for the target environment - no custom configuration templates or advanced features are required beyond basic installation
- The metadata-only dependency strategy was used for testing purposes - production deployment may require additional configuration management not visible in this simplified example
- Platform support is limited to Ubuntu 18.04+ and CentOS 7+ as declared in metadata - other distributions may require additional testing and configuration
- No custom nginx configuration files or templates are required beyond the basic installation and simple index page
- Redis configuration uses default settings - no custom redis.conf or advanced caching configurations are needed
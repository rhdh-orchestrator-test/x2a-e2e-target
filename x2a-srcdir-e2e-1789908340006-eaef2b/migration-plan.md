# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook infrastructure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration involves converting basic web server and caching service configurations to Ansible playbooks. This is a low-complexity migration with an estimated timeline of 1-2 weeks for a single engineer, suitable as a proof-of-concept for larger Chef-to-Ansible migrations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server installation with basic configuration, custom index page, and service management
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service enablement, static HTML content deployment, configurable port and worker processes

**cache**:
- Description: Redis server installation and configuration for caching services
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis package installation, service management, basic daemon configuration

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata with dependency declarations and platform support definitions
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform compatibility specifications
- `attributes/default.rb`: Default nginx configuration attributes including port, user, and worker process settings
- `README.md`: Documentation explaining metadata-only dependency strategy for testing purposes

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, plus nginx.nginx collection for advanced configuration
- **cache (local)**: Convert to Ansible role with redis installation and configuration tasks

### Security Considerations

- **File permissions**: Static HTML file creation uses explicit mode '0644' and root ownership - maintain these security practices in Ansible
- **Service management**: Both cookbooks use standard service management without custom security configurations
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the reviewed files
- **Network security**: Default nginx configuration exposes port 80 - consider SSL/TLS implementation in Ansible migration

### Technical Challenges

- **Dependency resolution**: The cookbook declares an external 'nginx' dependency that is not fetchable without Berksfile or Policyfile - will need to identify the specific nginx cookbook version and features used
- **Attribute translation**: Chef attributes system needs conversion to Ansible variables with proper precedence handling
- **Service ordering**: Ensure proper task ordering in Ansible playbooks to maintain the same installation and startup sequence
- **Platform compatibility**: Maintain support for both Ubuntu and CentOS package managers and service systems

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Convert Redis installation and service management to Ansible role
2. **simple-nginx cookbook** (moderate complexity) - Convert nginx installation, configuration, and content deployment to Ansible playbook with proper variable handling

### Assumptions

- The external 'nginx' dependency refers to a standard community nginx cookbook with basic installation and configuration capabilities
- The target environment will have package managers (apt/yum) available and properly configured
- The metadata-only dependency strategy indicates this is a test/example cookbook, suggesting simplified production requirements
- No custom nginx configuration files or templates are required beyond the basic service setup
- Redis configuration can remain at default settings as no custom configuration is specified in the cache cookbook
- The cookbook is designed for testing purposes, so production-grade features like SSL, monitoring, or backup strategies may not be required initially
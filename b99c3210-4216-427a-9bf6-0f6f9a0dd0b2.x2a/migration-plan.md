# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure designed for testing metadata-only dependency strategies. The migration involves converting two Chef cookbooks (simple-nginx and cache) to Ansible roles. This is a low-complexity migration with an estimated timeline of 1-2 days for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server cookbook with basic configuration, service management, and custom index page deployment
- Path: . (root cookbook)
- Technology: Chef
- Key Features: Package installation, service management, static file deployment, attribute-driven configuration

**cache**:
- Description: Redis cache server cookbook providing simple caching functionality as a local dependency
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Root cookbook metadata defining dependencies on 'cache' and 'nginx' cookbooks
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes (port, user, worker processes)
- `README.md`: Documentation explaining metadata-only dependency strategy testing purpose

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in cookbook metadata supports declarations)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **cache (local)**: Convert to Ansible role with redis package management
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules

### Security Considerations
- File permissions: The cookbook creates `/var/www/html/index.html` with mode 0644 and root ownership - ensure Ansible file module maintains proper permissions
- Service management: Both nginx and redis services are enabled and started - verify proper service state management in Ansible
- No secrets detected: No encrypted data bags, vault usage, or hardcoded credentials found in the repository

### Technical Challenges
- **Dependency resolution**: The cookbook depends on an external 'nginx' cookbook that is not present in the repository - this dependency will need to be resolved through Ansible Galaxy roles or custom implementation
- **Attribute translation**: Chef attributes need to be converted to Ansible variables with proper precedence handling
- **Service management**: Ensure proper service state management across different Linux distributions (Ubuntu vs CentOS)
- **Package naming**: Redis package name differs between distributions (redis-server vs redis) - requires conditional logic

### Migration Order
1. **cache cookbook** (low risk, no external dependencies)
2. **simple-nginx cookbook** (moderate complexity, depends on cache role)

### Assumptions
- The external 'nginx' cookbook dependency mentioned in metadata.rb is not critical for basic functionality since the recipe directly manages the nginx package
- Target systems have internet access for package installation
- The cookbook is intended for development/testing environments based on the simple configuration
- Default nginx configuration is sufficient (no custom nginx.conf templates are provided)
- Redis default configuration is acceptable (no custom redis.conf management)
- The metadata-only dependency strategy mentioned in README.md refers to Chef tooling and won't impact Ansible migration
- Platform support will be maintained for Ubuntu 18.04+ and CentOS 7.0+ in the Ansible implementation
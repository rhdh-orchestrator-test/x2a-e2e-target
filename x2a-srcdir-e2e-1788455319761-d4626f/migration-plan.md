# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with two cookbooks that demonstrate a metadata-only dependency strategy. The migration scope is relatively small but includes both a main cookbook and a local dependency cookbook. The estimated timeline is 1-2 weeks for a single engineer, with low to moderate complexity due to the straightforward nature of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server cookbook with basic configuration, service management, and custom index page creation
- Path: . (root directory)
- Technology: Chef
- Key Features: Nginx package installation, service enablement and startup, custom HTML index page creation, configurable port and worker processes

**cache**:
- Description: Redis cache server cookbook providing simple caching functionality as a local dependency
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server package installation, service management, basic cache infrastructure

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on 'cache' and 'nginx' cookbooks, platform support for Ubuntu 18.04+ and CentOS 7+
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes including port (80), user (www-data), and worker processes (auto)
- `recipes/default.rb`: Main nginx installation and configuration recipe
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management recipe
- `README.md`: Documentation explaining metadata-only dependency strategy for X2A Convertor testing

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate the local cache cookbook to an Ansible role within the same playbook structure
- **redis-server**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.redis module for advanced configuration

### Security Considerations

- **File permissions**: The current cookbook sets explicit file permissions (0644) for the index.html file - ensure Ansible file module maintains proper permissions
- **Service user management**: The nginx user configuration (www-data) needs to be properly handled in Ansible, considering different default users across distributions
- **No secrets detected**: No encrypted data bags, vault usage, or hardcoded credentials found in the current cookbook structure

### Technical Challenges

- **Cross-platform compatibility**: The cookbook supports both Ubuntu and CentOS - Ansible playbooks will need to handle package name differences (nginx vs nginx, redis-server vs redis)
- **Service name variations**: Redis service names differ between distributions (redis-server vs redis) - use ansible.builtin.service with appropriate conditionals
- **Dependency management**: The external 'nginx' cookbook dependency is declared but not resolvable - need to determine if this refers to a community cookbook or custom implementation
- **Attribute translation**: Chef attributes need to be converted to Ansible variables with appropriate default values and variable precedence

### Migration Order

1. **cache cookbook** (low risk, no external dependencies) - Migrate redis installation and service management first
2. **simple-nginx cookbook** (moderate complexity) - Migrate nginx installation, service management, and file creation after cache is complete
3. **Integration testing** - Verify both services work together and dependency relationships are maintained

### Assumptions

- The external 'nginx' cookbook dependency mentioned in metadata.rb is not critical for basic functionality, as the recipes only use built-in Chef resources
- The target environment will have internet access for package installation via apt/yum
- The migration will maintain the same service startup behavior (enable and start services)
- File paths (/var/www/html/index.html) are appropriate for the target environment and don't require customization
- The Chef version requirement (>= 16.0) indicates relatively modern infrastructure that should be compatible with current Ansible versions
- No custom templates or complex configuration files are required beyond the simple index.html file
- The metadata-only dependency strategy mentioned in the README suggests this is a test/example cookbook rather than production infrastructure
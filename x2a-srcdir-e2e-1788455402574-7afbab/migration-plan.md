# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small but demonstrates key Chef patterns including cookbook dependencies, attribute management, and service configuration. Estimated migration timeline: 1-2 weeks for a single developer, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**simple-nginx**:
- Description: Simple nginx web server cookbook with basic configuration, service management, and custom index page deployment
- Path: . (root directory)
- Technology: Chef
- Key Features: Package installation, service management (enable/start), static file deployment, attribute-driven configuration

**cache**:
- Description: Redis cache server cookbook providing caching services as a local dependency
- Path: cookbooks/cache
- Technology: Chef  
- Key Features: Redis server installation, service management (enable/start), basic cache functionality

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata defining dependencies on 'cache' (local) and 'nginx' (external) cookbooks, platform support for Ubuntu 18.04+ and CentOS 7+
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata with platform support definitions
- `attributes/default.rb`: Default nginx configuration attributes including port (80), user (www-data), and worker processes (auto)
- `recipes/default.rb`: Main nginx installation and configuration recipe with package, service, and file resources
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management recipe
- `README.md`: Documentation explaining metadata-only dependency strategy for X2A Convertor testing

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (explicitly supported in metadata.rb files)
- **Virtual Machine Technology**: Not specified in source configuration
- **Cloud Platform**: Not specified in source configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with ansible.builtin.package and ansible.builtin.service modules, or use community.general.nginx_* modules for advanced configuration
- **cache (local)**: Migrate the Redis installation logic to Ansible using ansible.builtin.package and ansible.builtin.service modules
- **Chef >= 16.0**: No direct equivalent needed in Ansible, but ensure target systems have Python 3.6+ for Ansible compatibility

### Security Considerations

- **File permissions**: The cookbook creates `/var/www/html/index.html` with mode 0644 and root ownership - ensure Ansible file module maintains proper permissions
- **Service management**: Both nginx and redis services are enabled and started - verify Ansible service module properly handles service security contexts
- **No secrets detected**: This cookbook contains no encrypted data bags, vault usage, or hardcoded credentials
- **Static content**: The index.html file contains static content with no dynamic secrets or sensitive information

### Technical Challenges

- **Attribute system migration**: Chef attributes (nginx.port, nginx.user, nginx.worker_processes) need to be converted to Ansible variables with proper precedence handling
- **Dependency resolution**: The external 'nginx' cookbook dependency needs to be replaced with appropriate Ansible roles or modules from Ansible Galaxy
- **Service state management**: Ensure Ansible properly handles the [:enable, :start] action pattern used in Chef service resources
- **Cross-platform support**: Maintain compatibility with both Ubuntu (apt) and CentOS (yum/dnf) package managers

### Migration Order

1. **cache cookbook** (low risk, no external dependencies)
   - Simple Redis installation and service management
   - Good starting point to establish Ansible patterns
   
2. **simple-nginx cookbook** (moderate complexity)
   - Depends on cache cookbook completion
   - Requires handling of external nginx dependency
   - More complex with attributes and file management

### Assumptions

- The external 'nginx' cookbook dependency mentioned in metadata.rb is not present in this repository and will need to be replaced with Ansible Galaxy roles or custom tasks
- Target systems will have appropriate package managers (apt for Ubuntu, yum/dnf for CentOS) configured and accessible
- The current Chef cookbook is designed for testing metadata-only dependency strategies, so production hardening may be needed
- No custom Chef resources or complex cookbook patterns are used, making migration straightforward
- The cookbook assumes standard web server directory structures (/var/www/html) exist on target systems
- Redis and nginx packages are available in standard distribution repositories
- No custom configuration files or templates are used beyond the simple index.html file creation
- The cookbook does not handle SSL/TLS configuration, firewall rules, or advanced nginx features
- Service management assumes systemd is available on target platforms (standard for Ubuntu 18.04+ and CentOS 7+)
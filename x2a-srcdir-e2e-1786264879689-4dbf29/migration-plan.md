# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef cookbook called "simple-nginx" that needs to be migrated to Ansible. The cookbook is relatively simple, focusing on installing and configuring Nginx with a basic HTML page. It has a local dependency on a "cache" cookbook that installs and configures Redis.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will need to handle these dependencies in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index.html file.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module to install Nginx
- **cache (1.0.0)**: Convert to an Ansible role that installs and configures Redis

### Security Considerations

- No explicit security configurations were identified in the source code
- No secrets management or credential patterns were detected
- Basic service configuration should follow Ansible security best practices

### Technical Challenges

- **Dependency Management**: The original cookbook relies on Chef's dependency resolution. Ansible handles dependencies differently, so we'll need to ensure proper role inclusion.
- **Configuration Management**: Converting Chef attributes to Ansible variables while maintaining the same functionality.
- **Service Management**: Ensuring services are properly enabled and started in the Ansible equivalent.

### Migration Order

1. **cache role** (Priority 1): Create an Ansible role for Redis installation and configuration
2. **nginx role** (Priority 2): Create an Ansible role for Nginx installation and configuration

### Assumptions

1. The cookbook is used in a simple deployment scenario without complex Chef-specific features
2. No custom resources or libraries are being used
3. The external 'nginx' dependency doesn't contain critical functionality beyond what's visible in the recipes
4. No complex templating or configuration is required beyond what's visible in the source files
5. No integration with external systems or services beyond Redis and Nginx
6. No secrets management or security-specific configurations are needed

## Migration Timeline Estimate

Given the simplicity of the cookbooks (two small cookbooks with basic functionality), the migration should be relatively straightforward:

- Analysis and planning: 1 day
- Development of Ansible roles: 2-3 days
- Testing and validation: 1-2 days
- Documentation: 1 day

Total estimated timeline: 5-7 business days for a complete migration.

## Migration Steps

1. Create an Ansible project structure with roles for 'nginx' and 'redis'
2. Convert Chef attributes to Ansible variables
3. Create tasks for package installation, service management, and file creation
4. Implement proper dependency handling between roles
5. Create comprehensive tests to validate functionality
6. Document the new Ansible roles and their usage
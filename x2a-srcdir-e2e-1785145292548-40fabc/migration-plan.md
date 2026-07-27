# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local cache dependency. The migration scope is relatively small, consisting of one main cookbook and one local dependency cookbook. Based on the analysis, this is a low-complexity migration that could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a simple welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server as a caching solution
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: The cookbooks support Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the metadata.rb files.
- **Virtual Machine Technology**: Not specified in the repository. Default to standard VM environments.
- **Cloud Platform**: No cloud-specific configurations are present in the repository.

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration
- **redis-server package**: Ensure proper package installation across different OS distributions using Ansible's package module with conditional logic

### Security Considerations

- No explicit security configurations or secrets management were identified in the repository.
- The Nginx configuration is basic and doesn't include SSL/TLS settings.
- No hardcoded credentials were found in the codebase.

### Technical Challenges

- **Platform Compatibility**: The Chef cookbooks support both Ubuntu and CentOS. The Ansible roles should maintain this compatibility using conditional tasks based on the `ansible_os_family` variable.
- **Dependency Management**: The external 'nginx' dependency needs to be properly addressed in Ansible, either by creating a custom role or using a community role with appropriate configuration.

### Migration Order

1. **cache role** (Priority 1): Convert the simple Redis installation and service management to an Ansible role first, as it's a dependency for the main cookbook.
2. **nginx role** (Priority 2): Convert the Nginx installation, configuration, and content creation to an Ansible role.
3. **playbook integration** (Priority 3): Create a main playbook that includes both roles and sets appropriate variables.

### Assumptions

1. The external 'nginx' dependency is a standard Chef cookbook without custom modifications.
2. No complex Chef resources or custom Ruby code is used beyond what's visible in the repository.
3. No Chef environments, data bags, or roles are in use for configuration management.
4. The simple HTML content in the index.html file doesn't need to be dynamically generated.
5. No specific Nginx configuration files are being managed beyond the basic installation and service.
6. Redis is being used with default configuration settings.
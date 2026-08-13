# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a simple welcome page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation task
- **cache (local)**: Migrate the Redis installation and configuration to Ansible tasks

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **Attribute Translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables
- **Service Management**: Chef service resources need to be translated to Ansible service modules
- **External Dependencies**: The external nginx dependency needs to be addressed in the Ansible structure

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation, configuration, and content deployment

### Ansible Structure Recommendation

```
simple-nginx/
├── defaults/
│   └── main.yml       # Convert Chef attributes to Ansible defaults
├── tasks/
│   ├── main.yml       # Main tasks from Chef recipes/default.rb
│   └── redis.yml      # Tasks from cache cookbook
├── templates/
│   └── index.html.j2  # Template for the welcome page
└── meta/
    └── main.yml       # Role metadata (from Chef metadata.rb)
```

### Implementation Plan

1. **Create Ansible Role Structure**:
   - Create the directory structure for the Ansible role
   - Convert Chef metadata to Ansible role metadata

2. **Migrate Attributes**:
   - Convert Chef attributes to Ansible variables in `defaults/main.yml`:
     ```yaml
     nginx_port: 80
     nginx_user: www-data
     nginx_worker_processes: auto
     ```

3. **Migrate Recipes to Tasks**:
   - Convert the Nginx installation and configuration from Chef to Ansible tasks
   - Convert the Redis installation and configuration from the cache cookbook

4. **Create Templates**:
   - Convert the static HTML content to an Ansible template

5. **Testing**:
   - Create a playbook to test the role
   - Verify functionality matches the original Chef cookbook

### Assumptions

- The cookbook is intended for basic Nginx and Redis installation without complex configurations
- No custom templates or additional files beyond what's visible in the repository
- No specific security requirements or hardening is needed
- The external nginx dependency is a standard cookbook without custom modifications
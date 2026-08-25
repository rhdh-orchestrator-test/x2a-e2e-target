# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with a basic configuration. The repository is relatively small and straightforward, consisting of a main cookbook with one local dependency (`cache` cookbook). The migration to Ansible should be of low complexity and can likely be completed within 1-2 days by a single developer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible metadata or requirements files.
- `attributes/default.rb`: Contains configuration variables for Nginx. These will be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management. Will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` module or community.general collection
- **cache (local)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Consider implementing TLS/SSL for Nginx in the Ansible role as a security enhancement

### Technical Challenges

- **External dependency handling**: The `nginx` dependency is declared but not included in the repository. The Ansible migration will need to either incorporate the functionality directly or use Ansible Galaxy for dependency management.
- **Configuration management**: Ensure that the Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, moderate complexity due to dependency on cache

### Assumptions

1. The external `nginx` dependency is used for advanced configuration not present in the simple-nginx cookbook itself
2. No custom templates or additional files are used beyond what's visible in the repository
3. No complex conditionals or platform-specific code exists in the recipes
4. No authentication or authorization mechanisms are implemented
5. No custom error pages or advanced Nginx configurations are required
6. The Redis cache is a standalone service and not configured for clustering or replication

## Ansible Migration Details

### Proposed Structure

```
simple-nginx/
├── defaults/
│   └── main.yml  # Variables from attributes/default.rb
├── meta/
│   └── main.yml  # Information from metadata.rb
├── tasks/
│   └── main.yml  # Logic from recipes/default.rb
└── README.md

roles/
└── cache/
    ├── defaults/
    │   └── main.yml
    ├── meta/
    │   └── main.yml
    ├── tasks/
    │   └── main.yml
    └── README.md
```

### Implementation Notes

1. Convert Chef resources to Ansible modules:
   - `package` resources → `apt`/`yum` modules
   - `service` resources → `service` module
   - `file` resources → `copy` or `template` modules

2. Convert Chef attributes to Ansible variables in `defaults/main.yml`

3. Create proper dependency management using Ansible Galaxy requirements

4. Implement idempotent tasks to match Chef's behavior

5. Consider using handlers for service restarts when configuration changes
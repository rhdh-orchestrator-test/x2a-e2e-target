# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook structure for an Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation task
- **cache (local)**: Migrate to Ansible tasks for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Basic service configuration without SSL/TLS implementation
- Vault/secrets management: No credentials detected in any module

### Technical Challenges

- **Attribute Translation**: Convert Chef attributes to Ansible variables
  - Nginx configuration attributes need to be mapped to Ansible variables
  - Mitigation: Create a vars file with equivalent settings

- **Service Management**: Ensure proper service management in Ansible
  - Both cookbooks manage services (nginx and redis-server)
  - Mitigation: Use Ansible service module with equivalent state management

### Migration Order

1. **cache cookbook** (Priority 1, low complexity)
   - Simple Redis installation and service configuration
   - No dependencies on other components

2. **simple-nginx cookbook** (Priority 2, depends on cache)
   - Nginx installation, configuration, and content deployment
   - Depends on the cache cookbook

### Assumptions

1. The external nginx dependency is used only for metadata purposes and not for actual functionality (as suggested by the README)
2. No complex configuration templates are used beyond the basic settings in attributes
3. No custom resources or libraries are implemented
4. No data bags or encrypted secrets are used
5. The cookbooks are designed for testing a "metadata-only dependency strategy" and may not represent a production deployment

## Ansible Migration Details

### Proposed Structure

```
simple-nginx/
├── defaults/
│   └── main.yml       # Variables (converted from attributes/default.rb)
├── tasks/
│   ├── main.yml       # Main tasks (converted from recipes/default.rb)
│   └── cache.yml      # Cache tasks (converted from cookbooks/cache/recipes/default.rb)
├── meta/
│   └── main.yml       # Role metadata (converted from metadata.rb)
└── templates/
    └── index.html.j2  # Template for index page
```

### Implementation Notes

1. Convert Chef resources to Ansible modules:
   - `package` resources → `apt`/`yum` modules
   - `service` resources → `service` module
   - `file` resources → `copy`/`template` modules

2. Convert Chef attributes to Ansible variables:
   - Move nginx configuration attributes to `defaults/main.yml`

3. Implement proper role dependencies:
   - Consider using Ansible Galaxy for the nginx dependency
   - Incorporate the cache functionality directly or as a separate role

4. Ensure idempotent execution:
   - Verify that all tasks are properly idempotent
   - Add appropriate state checking where needed
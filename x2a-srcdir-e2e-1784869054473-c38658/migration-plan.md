# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook structure with a main cookbook (simple-nginx) and one local dependency cookbook (cache). The migration scope is relatively small, with only two cookbooks that perform basic installation and configuration of nginx and redis. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation and basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and service management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service enablement

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible metadata in role or collection format.
- `attributes/default.rb`: Contains configuration parameters for nginx. Will be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe for nginx installation and configuration. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata. Will be replaced by Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Redis installation and service management. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation tasks
- **cache (local)**: Migrate the Redis installation and service management to Ansible tasks

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Standard service ports are used (nginx on port 80)
- No authentication mechanisms implemented for Redis, which may need to be addressed in the Ansible implementation

### Technical Challenges

- **Simple Migration**: The cookbooks are straightforward with minimal complexity, making migration relatively simple
- **Dependency Management**: The external nginx dependency will need to be replaced with appropriate Ansible tasks or roles
- **Testing**: Ensuring the migrated Ansible roles provide the same functionality as the original Chef cookbooks

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation, configuration, and content deployment

### Assumptions

1. The external nginx dependency is used only for installation and basic configuration
2. No complex templating or configuration management is required beyond what's visible in the code
3. No authentication or SSL/TLS configuration is needed
4. The simple HTML content is static and doesn't require dynamic generation
5. No custom nginx configurations beyond the basic attributes defined
6. No integration with other services beyond Redis
7. No specific user management or permissions beyond the default www-data user
8. No backup or maintenance procedures are implemented
9. No monitoring or logging configurations are present
10. The target environment will continue to be Ubuntu 18.04+ or CentOS 7+
11. Redis is used with default configuration settings

## Ansible Migration Details

### Proposed Structure

```
roles/
├── nginx/
│   ├── defaults/
│   │   └── main.yml  # Variables from attributes/default.rb
│   ├── tasks/
│   │   └── main.yml  # Logic from recipes/default.rb
│   ├── meta/
│   │   └── main.yml  # Information from metadata.rb
│   └── README.md
│
└── redis-cache/  # Migrated from cookbooks/cache
    ├── defaults/
    │   └── main.yml
    ├── tasks/
    │   └── main.yml
    └── meta/
        └── main.yml

playbooks/
└── site.yml  # Main playbook to apply both roles
```

### Implementation Notes

1. Convert Chef resources to equivalent Ansible modules:
   - `package` resources → `apt`/`yum` modules
   - `service` resources → `service` module
   - `file` resources → `file` or `copy` modules

2. Convert Chef attributes to Ansible variables in defaults/main.yml:
   ```yaml
   nginx_port: 80
   nginx_user: www-data
   nginx_worker_processes: auto
   ```

3. Implement proper idempotence checks to match Chef's behavior

4. Consider using existing Ansible Galaxy roles for nginx and redis to leverage community-maintained solutions

5. Implement proper dependency management between the roles if needed
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named "simple-nginx" that installs and configures Nginx with a basic welcome page. The cookbook follows a metadata-only dependency strategy and includes a local dependency on a "cache" cookbook that installs and configures Redis. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, configures the service, and creates a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including name, version, dependencies, and supported platforms
- `attributes/default.rb`: Contains default attributes for Nginx configuration (port, user, worker processes)
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **redis-server (unspecified version)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- No explicit security configurations identified in the current codebase
- Basic service configuration without authentication or TLS
- Vault/secrets management:
  - No credentials detected in the examined files
  - No encrypted data bags or Chef Vault usage identified

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collections.
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables, particularly the Nginx configuration attributes.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service configuration, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The cookbook is used in a development/testing environment given its simplicity and lack of security configurations
2. The external nginx dependency is used only for metadata purposes and not for actual functionality
3. No complex configuration templates are used beyond the basic setup shown in the recipes
4. No custom resources or libraries are used in the cookbooks
5. No data bags or encrypted secrets are used in the implementation
6. The target environment supports package managers (apt/yum) for installing nginx and redis-server

## Ansible Migration Details

### Proposed Structure

```
simple-nginx/
├── defaults/
│   └── main.yml  # Former Chef attributes
├── meta/
│   └── main.yml  # Dependencies
├── tasks/
│   └── main.yml  # Former Chef recipes
├── templates/
│   └── index.html.j2  # Template for index page
└── README.md

cache/
├── meta/
│   └── main.yml
└── tasks/
    └── main.yml  # Redis installation tasks
```

### Implementation Notes

1. Convert Chef attributes to Ansible variables in defaults/main.yml
2. Convert Chef resources to Ansible modules:
   - `package` resources → `ansible.builtin.package` module
   - `service` resources → `ansible.builtin.service` module
   - `file` resources → `ansible.builtin.copy` or `ansible.builtin.template` modules
3. Create a requirements.yml file to manage external dependencies
4. Implement proper idempotence checks for all tasks
5. Add proper documentation in README.md

### Testing Strategy

1. Create a simple playbook that includes both roles
2. Test on both Ubuntu and CentOS platforms as specified in the original metadata
3. Verify idempotence by running the playbook multiple times
4. Validate that Nginx and Redis services are running correctly
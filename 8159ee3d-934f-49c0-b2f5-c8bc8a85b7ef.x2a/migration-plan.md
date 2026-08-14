# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible metadata or requirements files.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for installing and configuring Nginx. Will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis. Will be converted to Ansible tasks.

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or create custom tasks using the `apt`/`yum` and `service` modules
- **cache (local)**: Convert to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current cookbooks
- Basic service configuration without authentication or encryption
- Vault/secrets management:
  - No credentials detected in the cookbooks
  - No SSL/TLS certificate references found
  - No encrypted data bags or Chef Vault usage identified

### Technical Challenges

- **Dependency Management**: The main cookbook depends on an external 'nginx' cookbook which is not included in the repository. The Ansible migration will need to implement the functionality directly rather than relying on external dependencies.
- **Configuration Management**: Ensure Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation, service management, and basic content creation

### Ansible Structure Recommendation

```
ansible-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # From file resource in recipes/default.rb
│   │   └── defaults/
│   │       └── main.yml  # From attributes/default.rb
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Any default variables
├── playbook.yml  # Main playbook calling roles
└── requirements.yml  # For any external role dependencies
```

### Assumptions

1. The external 'nginx' dependency is used only for installation and basic configuration, which can be implemented directly in Ansible.
2. No complex Chef-specific features (like search, data bags, environments) are being used in these cookbooks.
3. The cookbooks are intended for simple deployments without complex orchestration requirements.
4. No custom resources or libraries are being used that would require special handling in Ansible.
5. The Redis configuration in the cache cookbook uses default settings without customization.
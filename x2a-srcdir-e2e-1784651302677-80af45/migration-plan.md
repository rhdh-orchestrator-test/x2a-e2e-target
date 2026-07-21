# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook structure with a main cookbook called `simple-nginx` and a local dependency cookbook called `cache`. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and platform support. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains default attributes for the nginx configuration. Will need to be translated to Ansible role defaults.
- `recipes/default.rb`: Contains the main recipe for installing and configuring nginx. Will need to be translated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will need to be translated to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be translated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Firewall rules for nginx and Redis
  - Proper file permissions for web content
  - Redis password protection (not implemented in the original cookbook)
- Vault/secrets management: No credentials or secrets detected in the cookbooks

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collection dependencies.
- **Service Configuration**: Ensure proper translation of service management from Chef resources to Ansible service modules.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation, configuration, and content deployment

### Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   └── production/
│       ├── hosts
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── meta/
│   │       └── main.yml  # Converted from metadata.rb
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── meta/
│           └── main.yml  # Converted from cookbooks/cache/metadata.rb
├── playbooks/
│   └── site.yml
└── requirements.yml  # For external dependencies
```

### Assumptions

1. The nginx cookbook is intended for basic web server setup without complex configurations
2. The cache cookbook is intended to provide Redis as a caching layer for applications
3. No custom templates or complex configurations are needed beyond what's explicitly defined in the recipes
4. No secrets management or sensitive data handling is required
5. The cookbooks are designed for testing purposes and may need additional features for production use
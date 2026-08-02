# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` with a local dependency on a `cache` cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, and simple index page creation

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration will require mapping these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains Nginx configuration attributes that will need to be converted to Ansible variables.
- `README.md`: Documentation file that should be updated to reflect the Ansible migration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy community.nginx role or create a custom Nginx role
- **cache (local)**: Create an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No credentials or secrets management was detected
- Standard service security practices should be applied in the Ansible roles

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collection dependencies.
- **Configuration Management**: Converting Chef attributes to Ansible variables while maintaining the same functionality.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration, depends on cache

### Ansible Migration Structure

Proposed Ansible structure:

```
ansible-simple-nginx/
├── inventories/
│   └── development/
│       ├── group_vars/
│       │   └── all.yml  # Variables from attributes/default.rb
│       └── hosts
├── roles/
│   ├── cache/           # Migrated from cookbooks/cache
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   └── tasks/
│   │       └── main.yml # Redis installation tasks
│   └── nginx/           # Migrated from root cookbook
│       ├── defaults/
│       │   └── main.yml # Variables from attributes/default.rb
│       ├── tasks/
│       │   └── main.yml # Nginx installation tasks
│       └── templates/
│           └── index.html.j2
├── site.yml             # Main playbook
└── requirements.yml     # External dependencies
```

### Assumptions

1. The cookbook is intended for testing purposes only, as indicated in the README.
2. The external 'nginx' dependency is not available in the repository and would need to be sourced separately.
3. No complex configuration or customization is required beyond the basic installation and service management.
4. No specific security requirements or hardening is needed for this migration.
5. The target environment supports both Ubuntu 18.04+ and CentOS 7.0+ as specified in the metadata.
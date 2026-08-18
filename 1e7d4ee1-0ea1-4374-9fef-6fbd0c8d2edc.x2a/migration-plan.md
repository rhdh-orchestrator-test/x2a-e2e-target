# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

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

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration considerations: Dependencies will need to be mapped to Ansible roles or collections.
- `attributes/default.rb`: Contains default attributes for nginx configuration. Migration considerations: These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for nginx installation and configuration. Migration considerations: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for cache cookbook. Migration considerations: Will need to be converted to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for redis installation and service management. Migration considerations: Convert to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.nginx collection or create a custom Ansible role
- **redis-server (unspecified version)**: Replace with Ansible community.redis collection or create a custom Ansible role

### Security Considerations

- No explicit security configurations identified in the current cookbooks
- No vault/secrets management detected
- Standard service security considerations for nginx and redis should be addressed in the Ansible roles

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The Ansible migration will need to either incorporate this functionality directly or use the community.nginx collection.
- **Configuration management**: Ensure that the nginx configuration parameters from attributes/default.rb are properly mapped to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity, no dependencies
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The cookbooks are used in a simple deployment scenario without complex orchestration
2. No custom resources or libraries are being used (none were found in the repository)
3. The nginx external dependency is handled through a standard Chef Supermarket dependency
4. No complex configuration templates are required (none were found in the repository)
5. No secrets management or security hardening is implemented in the current cookbooks

## Ansible Migration Structure

### Proposed Ansible Structure

```
ansible-nginx/
├── inventories/
│   └── default/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # From attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # From recipes/default.rb
│   │   └── meta/
│   │       └── main.yml  # From metadata.rb
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── meta/
│           └── main.yml  # From cookbooks/cache/metadata.rb
├── playbook.yml  # Main playbook that includes both roles
└── README.md
```

### Implementation Notes

1. Convert Chef package, service, and file resources to equivalent Ansible modules
2. Map Chef attributes to Ansible variables
3. Create a main playbook that includes both roles in the correct order
4. Document any assumptions or manual steps required for deployment
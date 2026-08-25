# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook "simple-nginx" and a local dependency cookbook "cache". The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

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
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and platform support. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be translated to Ansible role defaults.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be translated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will need to be translated to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be translated to Ansible tasks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current cookbooks
- No secrets management or credential patterns detected
- Basic service configuration should follow Ansible security best practices

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through requirements.yml or collection dependencies.
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and configuration, no dependencies
2. **nginx role** (Priority 2): Depends on cache role, but still relatively simple

### Assumptions

1. The external nginx dependency is a standard Chef cookbook and doesn't contain custom modifications
2. No complex Chef-specific features (like search, data bags, etc.) are being used
3. The cookbooks are intended for Ubuntu 18.04+ and CentOS 7.0+ as specified in the metadata
4. No specific configuration templates are being used beyond the basic package installation and service management
5. No complex conditionals or platform-specific logic is implemented

## Ansible Structure Recommendation

```
ansible-simple-nginx/
├── collections/
│   └── requirements.yml  # For external collection dependencies
├── inventory/
│   └── hosts.yml         # Target hosts inventory
├── roles/
│   ├── nginx/            # Migrated from simple-nginx cookbook
│   │   ├── defaults/
│   │   │   └── main.yml  # Migrated from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Migrated from metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Migrated from recipes/default.rb
│   │   └── templates/    # For any template files
│   └── redis/            # Migrated from cache cookbook
│       ├── meta/
│       │   └── main.yml  # Migrated from cookbooks/cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Migrated from cookbooks/cache/recipes/default.rb
└── site.yml              # Main playbook
```

## Migration Steps

1. Create the Ansible directory structure as outlined above
2. Create the nginx role:
   - Convert attributes/default.rb to roles/nginx/defaults/main.yml
   - Convert recipes/default.rb to roles/nginx/tasks/main.yml
   - Create roles/nginx/meta/main.yml based on metadata.rb
3. Create the redis role:
   - Convert cookbooks/cache/recipes/default.rb to roles/redis/tasks/main.yml
   - Create roles/redis/meta/main.yml based on cookbooks/cache/metadata.rb
4. Create a site.yml playbook that includes both roles
5. Test the playbook against supported platforms (Ubuntu 18.04+ and CentOS 7.0+)
6. Document any platform-specific considerations or requirements

This migration is relatively straightforward due to the simplicity of the cookbooks and the absence of complex Chef-specific features.
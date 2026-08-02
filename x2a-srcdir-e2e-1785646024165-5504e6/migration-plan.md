# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a simple welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' (local) and 'nginx' (external). Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role such as `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current cookbooks
- Standard web server security practices should be implemented in the Ansible roles:
  - Firewall configuration for ports 80/443
  - TLS/SSL certificate management
  - Proper file permissions for web content
- Vault/secrets management:
  - No credentials were detected in the examined files

### Technical Challenges

- **Dependency Management**: The external 'nginx' dependency needs to be replaced with an appropriate Ansible Galaxy role or custom implementation
- **Configuration Translation**: Nginx attributes need to be mapped to Ansible variables with equivalent functionality
- **Service Management**: Ensure proper service management across different OS platforms (Ubuntu/CentOS)

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation with configuration from attributes

### Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── redis_cache/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
└── playbook.yml
```

### Assumptions

- The cookbook is intended for basic Nginx and Redis installation without complex configurations
- No custom templates or additional files beyond what's visible in the repository
- No specific security requirements beyond standard practices
- No complex integration between Nginx and Redis beyond coexistence on the same system
- External 'nginx' dependency is used for additional Nginx configurations not present in the simple-nginx cookbook
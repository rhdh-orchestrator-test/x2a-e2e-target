# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx deployment with a local cache dependency. The migration scope is relatively small, consisting of one main cookbook with a single local dependency. Based on the repository analysis, this is a straightforward migration that could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. This will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Standard service ports are used (port 80 for Nginx)
- No SSL/TLS configurations were found

### Technical Challenges

- **External dependency handling**: The 'nginx' dependency is declared but not included in the repository. The migration will need to determine the exact requirements and configurations needed from this dependency.
- **Configuration management**: Ensure that the Nginx configuration attributes are properly translated to Ansible variables with appropriate defaults.

### Migration Order

1. **cache role** (Priority 1): Convert the Redis cache cookbook to an Ansible role first as it's a dependency for the main cookbook
2. **nginx role** (Priority 2): Convert the main Nginx cookbook to an Ansible role

### Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # Converted from file resource
│   │   └── defaults/
│   │       └── main.yml  # Default variables
│   └── cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Default variables
└── site.yml  # Main playbook
```

### Assumptions

1. The external 'nginx' dependency is used for additional Nginx configurations not present in the main cookbook
2. No complex Chef-specific features (like search, data bags, or environments) are being used
3. The cookbooks are intended for Ubuntu/CentOS systems as specified in the metadata
4. No custom templates or additional files beyond what's visible in the repository are required
5. No complex runtime dependencies or ordering requirements exist between the cookbooks
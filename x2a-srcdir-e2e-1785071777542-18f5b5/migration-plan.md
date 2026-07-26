# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local cache dependency. The migration scope is relatively small, consisting of one main cookbook and one local dependency cookbook. Based on the repository analysis, this is a straightforward migration that could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. This should be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. This should be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible community.general.nginx or a custom Ansible role
- **cache (1.0.0)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Standard service security practices should be applied in the Ansible roles

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook that is not included in the repository. The Ansible migration will need to implement the functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: Ensure that the Nginx configuration parameters from attributes/default.rb are properly mapped to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Convert to an Ansible role for Redis installation first as it's a dependency
2. **simple-nginx cookbook** (Priority 2): Convert to an Ansible role for Nginx installation and configuration

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
│   │   │   └── index.html.j2  # From the file resource in recipes/default.rb
│   │   └── defaults/
│   │       └── main.yml  # From attributes/default.rb
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # From cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Any default variables
├── playbook.yml
└── README.md
```

### Assumptions

1. The external 'nginx' cookbook dependency is used for advanced configuration not visible in the current repository
2. No custom templates or additional files are needed beyond what's explicitly defined in the recipes
3. No complex conditionals or platform-specific code exists in the recipes
4. No secrets or sensitive data management is required
5. The Redis configuration uses default settings with no customization

## Migration Timeline Estimate

Given the simplicity of the cookbooks:

- Analysis and planning: 2 hours
- Role development: 4 hours
- Testing: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1.5 days)
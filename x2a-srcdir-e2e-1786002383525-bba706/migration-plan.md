# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with a simple welcome page. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with only two cookbooks to migrate: the main `simple-nginx` cookbook and its local dependency `cache` cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, configures it, and creates a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Defines default attributes for Nginx configuration
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role from Ansible Galaxy or create a custom role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current cookbooks
- No credentials or secrets management detected
- Standard service configurations without specific security hardening

### Technical Challenges

- **Dependency Management**: The original cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through role requirements or collections.
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables, particularly the Nginx configuration attributes.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and configuration, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The external `nginx` dependency is used only for its resources and not directly included in recipes
2. No complex Chef-specific features (like search, data bags, environments) are being used
3. No custom resources or libraries are present
4. The cookbooks are intended for basic installation and configuration without advanced customization
5. No CI/CD pipeline integration is present in the current implementation
6. No specific testing framework is being used

## Ansible Migration Details

### Proposed Structure

```
ansible-nginx/
├── inventories/
│   └── development/
│       ├── hosts
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
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Converted from cache cookbook
│       └── defaults/
│           └── main.yml
└── playbook.yml  # Main playbook that includes both roles
```

### Variable Mapping

Chef attributes will be converted to Ansible variables:

```yaml
# defaults/main.yml for nginx role
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Implementation Timeline

- **Day 1**: Create Ansible roles structure, convert recipes to tasks, and attributes to variables
- **Day 2**: Test the roles, create playbooks, and document the migration

### Testing Strategy

1. Create a test VM matching the supported platforms (Ubuntu 18.04+ or CentOS 7.0+)
2. Run the Ansible playbook against the test VM
3. Verify Nginx and Redis are installed and running
4. Verify the welcome page is accessible
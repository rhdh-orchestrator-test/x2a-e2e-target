# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a cache cookbook. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the straightforward nature of the configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content
    - Verified Path: recipes/default.rb exists (confirmed via list_directory)

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management
    - Verified Path: cookbooks/cache/recipes/default.rb exists (confirmed via list_directory)

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `README.md`: Documentation file explaining the cookbook's purpose and structure.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (1.0.0)**: Migrate the local cache cookbook to an Ansible role for Redis installation

### Security Considerations

- No explicit security configurations identified in the current codebase
- No vault/secrets management detected
- Standard service ports (80 for Nginx, default for Redis) should be reviewed for security best practices

### Technical Challenges

- **External Dependency**: The 'nginx' cookbook is referenced but not included in the repository. Need to determine exact functionality provided by this dependency to properly replicate in Ansible.
- **Configuration Management**: Ensure that Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Depends on cache, moderate complexity

### Assumptions

1. The 'nginx' external dependency is used only for basic Nginx installation and not for complex configurations
2. No custom templates or additional files are used beyond what's visible in the repository
3. No complex Chef-specific features (like search, data bags, environments) are being used
4. The Redis configuration uses default settings with no customization
5. No specific security hardening is implemented in the current cookbooks

## Ansible Migration Details

### Proposed Structure

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   └── tasks/
│   │       └── main.yml
│   └── redis_cache/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml
└── site.yml
```

### Variable Mapping

Chef attributes should be converted to Ansible variables:

```yaml
# group_vars/all.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Implementation Timeline

1. **Day 1**: 
   - Set up Ansible project structure
   - Create Redis cache role
   - Create Nginx role
   - Implement basic playbook

2. **Day 2**:
   - Testing and validation
   - Documentation
   - Knowledge transfer

### Testing Strategy

1. Deploy to test environment using Ansible
2. Verify Nginx installation and configuration
3. Verify Redis installation and service status
4. Validate web content is properly served
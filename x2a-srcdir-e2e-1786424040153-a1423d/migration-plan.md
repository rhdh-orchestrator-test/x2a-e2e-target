# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. Based on the complexity and size, this migration could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation for caching functionality
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. These should be converted to Ansible variables.
- `README.md`: Documentation file explaining the cookbook's purpose and structure. Should be updated to reflect the Ansible role.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or secrets management were identified in the repository
- Standard service security practices should be implemented in the Ansible roles:
  - Firewall rules for Nginx (port 80) and Redis
  - Redis password protection (not implemented in the original cookbook)

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: Ensure that the Nginx configuration attributes from `attributes/default.rb` are properly translated to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management
2. **nginx role** (Priority 2): Nginx installation with configuration from attributes

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Port, user, worker_processes variables
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation, service, and content tasks
│   │   └── templates/
│   │       └── index.html.j2  # Template for index page
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Redis installation and service tasks
│       └── defaults/
│           └── main.yml  # Redis configuration variables
└── playbook.yml  # Main playbook applying both roles
```

### Assumptions

1. The external 'nginx' dependency likely provides additional Nginx configuration beyond the basic package installation in the simple-nginx cookbook.
2. No custom Nginx configuration files are being managed beyond the basic installation and service enablement.
3. The Redis cache is used by the Nginx server, though the connection between them is not explicitly configured in the cookbooks.
4. No specific security hardening or customization is required beyond the basic installation.
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+ as specified in the metadata files.
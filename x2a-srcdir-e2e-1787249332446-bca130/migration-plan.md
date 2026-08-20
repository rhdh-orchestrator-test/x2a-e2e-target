# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for an Nginx web server with Redis caching. The migration scope is relatively small, consisting of one main cookbook with a local dependency. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, configures the service, and creates a basic index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should map these dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration parameters for Nginx including port, user, and worker processes. These should be converted to Ansible variables.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible community.nginx collection or create a custom Nginx role
- **cache (1.0.0)**: Migrate the local cache cookbook to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the codebase
- No credential patterns or secrets management were detected
- Basic service security should be implemented in the Ansible roles:
  - Nginx configuration should include secure defaults
  - Redis should be configured with authentication if exposed beyond localhost

### Technical Challenges

- **Dependency Resolution**: The external 'nginx' dependency is declared but not included in the repository. The Ansible migration will need to either:
  1. Create a custom Nginx role based on the implied requirements
  2. Use the community.nginx collection with appropriate configuration

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service configuration
2. **nginx role** (Priority 2): Web server configuration with appropriate variables

### Assumptions

1. The cookbook is designed for testing a "metadata-only dependency strategy" as mentioned in the README, suggesting this is a simplified example rather than a production configuration
2. The external 'nginx' dependency is expected to handle more complex Nginx configurations not present in the simple-nginx cookbook
3. No custom templates or complex configurations are present, making this a straightforward migration
4. No explicit security hardening is implemented in the current cookbooks
5. The cookbook appears to be a test or example cookbook rather than a production deployment

## Migration Implementation Details

### Ansible Structure

```
simple-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── defaults/
│   │       └── main.yml  # Default variables
│   └── redis_cache/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml  # Default variables
└── site.yml  # Main playbook
```

### Variable Mapping

Chef attributes should be converted to Ansible variables:

```yaml
# group_vars/all.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Task Conversion Examples

The Chef resources should be converted to Ansible tasks:

```yaml
# roles/nginx/tasks/main.yml
---
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Ensure nginx service is running
  service:
    name: nginx
    state: started
    enabled: yes

- name: Create a simple index page
  copy:
    content: "<h1>Welcome to Nginx - Ansible Migration</h1>"
    dest: /var/www/html/index.html
    mode: '0644'
    owner: root
    group: root
```

```yaml
# roles/redis_cache/tasks/main.yml
---
- name: Install redis-server
  package:
    name: redis-server
    state: present

- name: Ensure redis-server is running
  service:
    name: redis-server
    state: started
    enabled: yes
```

### Main Playbook

```yaml
# site.yml
---
- hosts: all
  become: yes
  roles:
    - redis_cache
    - nginx
```
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The main cookbook installs and configures Nginx with basic settings, while the cache cookbook installs and configures Redis. The migration scope is relatively small and straightforward, with an estimated timeline of 1-2 days for complete migration to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, simple index page creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible role metadata.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be converted to Ansible variables.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations identified in the current codebase
- No secrets management or credential patterns detected
- Standard service ports (Nginx on port 80, Redis on default port) should be reviewed for security

### Technical Challenges

- **External dependency**: The `nginx` dependency is declared but not included in the repository. The migration will need to either:
  1. Use an existing Ansible Galaxy role for Nginx
  2. Create a custom Nginx role based on the requirements
  3. Incorporate Nginx configuration directly into the main role

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration

### Ansible Structure Recommendation

```
ansible-project/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── nginx/   # Converted from simple-nginx cookbook
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── templates/
│   │   │   └── index.html.j2
│   │   └── meta/
│   │       └── main.yml
│   └── redis/   # Converted from cache cookbook
│       ├── tasks/
│       │   └── main.yml
│       └── meta/
│           └── main.yml
└── site.yml     # Main playbook
```

### Conversion Details

#### simple-nginx to Ansible Role

**Variables (from attributes/default.rb):**
```yaml
# roles/nginx/defaults/main.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

**Tasks (from recipes/default.rb):**
```yaml
# roles/nginx/tasks/main.yml
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

#### cache to Ansible Role

**Tasks (from cookbooks/cache/recipes/default.rb):**
```yaml
# roles/redis/tasks/main.yml
- name: Install redis
  package:
    name: redis-server
    state: present

- name: Ensure redis service is running
  service:
    name: redis-server
    state: started
    enabled: yes
```

### Assumptions

1. The external `nginx` dependency doesn't include complex configurations that would require additional investigation
2. No custom templates or files are being used beyond what's visible in the repository
3. No complex attribute overrides or environment-specific configurations exist
4. No integration with external systems or services beyond basic Nginx and Redis
5. No specific security requirements beyond standard service configurations
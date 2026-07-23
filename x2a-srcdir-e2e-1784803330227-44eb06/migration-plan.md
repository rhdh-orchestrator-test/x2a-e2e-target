# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` that installs and configures Nginx with basic settings. The migration scope is relatively small, with one main cookbook and one local dependency cookbook. Based on the repository analysis, this is a low-complexity migration that could be completed in approximately 1-2 days by a single developer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be translated to Ansible role defaults in defaults/main.yml.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be translated to Ansible tasks in tasks/main.yml.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the repository
- No secrets management or credential patterns were detected
- Basic file permissions are set for the index.html file (mode '0644')

### Technical Challenges

- **Dependency Management**: The Chef cookbook relies on an external 'nginx' dependency that is declared but not included. The Ansible migration will need to either incorporate this functionality directly or use an Ansible Galaxy role.
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Ansible Structure Plan

```
ansible-simple-nginx/
├── README.md
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Converted from attributes/default.rb
│   │   ├── meta/
│   │   │   └── main.yml  # Converted from metadata.rb
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   └── templates/
│   │       └── index.html.j2  # Converted from file resource
│   └── cache/
│       ├── meta/
│       │   └── main.yml  # Converted from cookbooks/cache/metadata.rb
│       └── tasks/
│           └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
└── playbook.yml  # New playbook to orchestrate roles
```

### Sample Ansible Conversions

**1. Chef attributes to Ansible defaults (defaults/main.yml):**
```yaml
---
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

**2. Chef recipe to Ansible tasks (tasks/main.yml):**
```yaml
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

**3. Chef metadata to Ansible meta (meta/main.yml):**
```yaml
---
galaxy_info:
  role_name: nginx
  author: Ansible Migration
  description: Simple nginx role migrated from Chef cookbook
  license: Apache-2.0
  min_ansible_version: 2.9
  platforms:
    - name: Ubuntu
      versions:
        - bionic
        - focal
    - name: EL
      versions:
        - 7
        - 8
  galaxy_tags:
    - web
    - nginx

dependencies:
  - role: cache
```

### Assumptions

- The Chef cookbook is intended for a simple Nginx installation without complex configurations
- The external 'nginx' dependency is used for additional Nginx configuration not present in the repository
- The cache cookbook is used to provide Redis caching capabilities for the Nginx server
- No custom templates or additional files beyond what's visible in the repository are required
- No complex Chef-specific features (like search, data bags, or environments) are being used
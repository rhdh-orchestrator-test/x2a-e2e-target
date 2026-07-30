# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (simple-nginx) and one local dependency cookbook (cache). The migration scope is relatively small, with two cookbooks that handle basic nginx and redis server installations. Based on the repository analysis, this migration is estimated to be low complexity and could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will be replaced by Ansible role metadata.
- `attributes/default.rb`: Contains configuration variables for nginx. Will be migrated to Ansible role defaults.
- `recipes/default.rb`: Contains the main nginx installation and configuration logic. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **cache (local)**: Migrate to a custom Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No credential patterns or secrets management were detected
- Basic service configuration should follow Ansible security best practices

### Technical Challenges

- **Dependency Management**: The original cookbook relies on an external nginx dependency that is declared but not included. The migration will need to either incorporate the nginx installation tasks directly or use an Ansible Galaxy role.
- **Configuration Management**: Ensure that the nginx configuration parameters from attributes are properly mapped to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The external nginx cookbook was used primarily for installation and basic configuration, which can be replaced with standard Ansible tasks or a community role.
2. No complex templating or advanced configurations are present in the external dependencies.
3. The cookbooks are designed for Ubuntu 18.04+ or CentOS 7+ as specified in the metadata.
4. No custom resources or libraries are being used that would require special handling.
5. No secrets management or security-specific configurations are present.
6. The simple HTML content in the nginx configuration is static and doesn't require dynamic templating.

## Migration Implementation Details

### For simple-nginx:

```yaml
# roles/nginx/defaults/main.yml
---
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

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
    content: '<h1>Welcome to Nginx - Metadata Only Example</h1>'
    dest: /var/www/html/index.html
    mode: '0644'
    owner: root
    group: root
```

### For cache:

```yaml
# roles/redis/tasks/main.yml
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

### Main Playbook:

```yaml
# site.yml
---
- hosts: all
  become: yes
  roles:
    - redis
    - nginx
```
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with two cookbooks that have straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and platform support. Will need to be translated to Ansible role metadata in meta/main.yml.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will be migrated to Ansible role defaults.
- `recipes/default.rb`: Main recipe for Nginx installation and configuration. Will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook. Will be translated to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management. Will be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` module or community.general collection
- **cache (local)**: Migrate to a separate Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Consider implementing TLS/SSL for Nginx in the Ansible role

### Technical Challenges

- **External dependency handling**: The `nginx` dependency is declared but not included in the repository. The Ansible migration will need to either include this functionality directly or establish a dependency on an external Ansible role.
- **Configuration management**: Ensure Nginx configuration parameters from attributes are properly translated to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Ansible Structure Recommendation

```
ansible-nginx/
├── README.md
├── defaults/
│   └── main.yml        # Converted from attributes/default.rb
├── meta/
│   └── main.yml        # Converted from metadata.rb
├── tasks/
│   └── main.yml        # Converted from recipes/default.rb
└── templates/
    └── index.html.j2   # Template for the welcome page

ansible-redis-cache/
├── README.md
├── meta/
│   └── main.yml        # Converted from cookbooks/cache/metadata.rb
└── tasks/
    └── main.yml        # Converted from cookbooks/cache/recipes/default.rb
```

### Conversion Details

#### simple-nginx to ansible-nginx

1. Convert attributes to defaults/main.yml:
```yaml
---
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

2. Convert recipe to tasks/main.yml:
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

#### cache to ansible-redis-cache

1. Convert recipe to tasks/main.yml:
```yaml
---
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

- The cookbooks are intended for Ubuntu 18.04+ or CentOS 7+ environments
- No custom Nginx configuration beyond the default installation is required
- No custom Redis configuration beyond the default installation is required
- No authentication or security measures are implemented in the current setup
- The welcome page content is static and doesn't require dynamic templating
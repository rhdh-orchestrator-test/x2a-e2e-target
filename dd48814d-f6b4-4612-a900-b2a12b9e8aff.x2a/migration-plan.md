# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server cookbook that installs Nginx, ensures the service is running, and creates a basic index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple Redis cache server cookbook that installs and configures Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
  - Migration consideration: Convert dependencies to Ansible Galaxy requirements
  
- `attributes/default.rb`: Contains default attributes for Nginx configuration
  - Migration consideration: Convert to Ansible variables in defaults/main.yml

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate to a custom Ansible Redis role or use `geerlingguy.redis` from Galaxy

### Security Considerations

- No explicit security configurations identified in the current cookbooks
- No credential patterns detected in the examined files
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions

### Technical Challenges

- **Simple Migration**: The cookbooks are straightforward with minimal complexity
- **Attribute Translation**: Convert Chef attributes to Ansible variables, maintaining the same structure
- **Service Management**: Ensure proper service management in Ansible for both Nginx and Redis

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with dependency on cache

### Assumptions

1. The external `nginx` dependency is a standard Chef cookbook that can be replaced with an Ansible Galaxy role
2. No complex configurations or templates are used beyond what's visible in the repository
3. No custom resources or libraries are used in the cookbooks
4. No secrets management or security-specific configurations are required
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+

## Migration Implementation Details

### For simple-nginx:

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
    content: '<h1>Welcome to Nginx - Metadata Only Example</h1>'
    dest: /var/www/html/index.html
    mode: '0644'
    owner: root
    group: root
```

```yaml
# roles/nginx/defaults/main.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### For cache:

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

### requirements.yml:

```yaml
---
roles:
  - name: geerlingguy.nginx
    version: 3.1.0
```

## Testing Strategy

1. Create Ansible playbooks that replicate the functionality of each Chef cookbook
2. Test on both Ubuntu and CentOS platforms as specified in the original metadata
3. Verify that Nginx and Redis services are properly installed and running
4. Confirm the index.html file is created with the correct content
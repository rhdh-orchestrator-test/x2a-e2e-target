# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (`simple-nginx`) and one local dependency cookbook (`cache`). The migration scope is relatively small, with only two cookbooks to convert. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks and their functionality.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis cache server installation and configuration
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Main cookbook metadata file defining dependencies and supported platforms
- `attributes/default.rb`: Default attributes for Nginx configuration
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata
- `cookbooks/cache/recipes/default.rb`: Cache cookbook recipe for Redis installation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 18.04+ and CentOS 7.0+ (explicitly defined in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (version unspecified)**: Replace with Ansible's `nginx` module or role
- **cache (1.0.0)**: Local cookbook to be migrated to an Ansible role for Redis installation

### Security Considerations

- No explicit security configurations identified in the current codebase
- Basic file permissions are set for the index.html file (mode '0644')
- Vault/secrets management:
  - No credentials or secrets detected in the repository
  - No encrypted data bags or Chef Vault usage identified

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook that is not included in the repository. The Ansible migration will need to implement this functionality directly.
- **Attribute Management**: Nginx configuration attributes will need to be converted to Ansible variables.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation role with minimal complexity
2. **nginx role** (Priority 2): Main web server role with configuration from attributes

### Assumptions

1. The external 'nginx' dependency is used for advanced configuration not visible in the current codebase
2. No complex Chef resources or custom resources are being used beyond what's visible in the recipes
3. No Berksfile or Policyfile is present, suggesting a simple dependency management approach
4. The cookbooks are designed for testing a "metadata-only dependency strategy" as mentioned in the README
5. No complex templating or configuration management is required beyond basic package installation and service management

## Migration Implementation Plan

### 1. Create Ansible Role Structure

```
roles/
  nginx/
    defaults/
      main.yml  # Convert Chef attributes
    tasks/
      main.yml  # Convert Chef recipes
    meta/
      main.yml  # Dependencies
  redis_cache/
    tasks/
      main.yml  # Convert cache cookbook
    meta/
      main.yml  # Dependencies
```

### 2. Convert Chef Attributes to Ansible Variables

```yaml
# roles/nginx/defaults/main.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### 3. Convert Chef Recipes to Ansible Tasks

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

```yaml
# roles/redis_cache/tasks/main.yml
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

### 4. Create Main Playbook

```yaml
# site.yml
---
- hosts: webservers
  roles:
    - redis_cache
    - nginx
```

### 5. Testing Strategy

1. Test each role individually
2. Test the complete playbook
3. Verify Nginx and Redis services are running correctly
4. Validate the index page is accessible

### 6. Documentation

Create documentation for the new Ansible roles, including:
- Role variables
- Dependencies
- Example usage
- Supported platforms
# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named "simple-nginx" that installs and configures Nginx web server with basic settings. The migration scope is relatively small, consisting of one main cookbook and one local dependency cookbook. Based on the analysis, this is a low-complexity migration that could be completed in approximately 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Redis server installation and configuration for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

**CRITICAL PATH VERIFICATION:**
- Verified that recipes/default.rb exists in the root directory
- Verified that cookbooks/cache/recipes/default.rb exists
- No Puppet modules (manifests/init.pp) were found in the repository
- No PowerShell modules (.psd1) were found in the repository

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible metadata or requirements files.
- `attributes/default.rb`: Contains default configuration values for Nginx. These will need to be migrated to Ansible variables.
- `recipes/default.rb`: Contains the main Chef recipe for installing and configuring Nginx. This will be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Contains the Redis installation and configuration recipe.

### Target Details

Based on the source configuration files:

- **Operating System**: The cookbook supports Ubuntu 18.04+ and CentOS 7.0+, as specified in the metadata.rb file.
- **Virtual Machine Technology**: Not specified in the repository.
- **Cloud Platform**: Not specified in the repository.

## Migration Approach

### Key Dependencies to Address

- **nginx (version not specified)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role for Nginx
- **cache (1.0.0)**: Migrate the local cache cookbook to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the cookbooks.
- No credential patterns or secrets management were detected.
- Basic file permissions are set for the index.html file (mode '0644').

### Technical Challenges

- **External Dependency**: The cookbook depends on an external 'nginx' cookbook which is not included in the repository. The migration will need to either:
  1. Create a custom Ansible role based on the functionality expected from this dependency
  2. Use an existing Ansible Galaxy role that provides similar functionality
  3. Consult with the team to understand the specific requirements from this dependency

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Depends on the cache cookbook, moderate complexity

### Assumptions

1. The 'nginx' external dependency is used for additional Nginx configuration not visible in the current repository.
2. The Redis cache configuration is minimal and doesn't include advanced settings.
3. There are no custom templates or additional files beyond what's visible in the repository.
4. No specific security hardening or custom configurations are applied to either Nginx or Redis.
5. The cookbooks are designed for basic installation and service management rather than complex configuration.

## Ansible Migration Details

### Proposed Ansible Structure

```
simple-nginx/
├── defaults/
│   └── main.yml       # Variables from attributes/default.rb
├── meta/
│   └── main.yml       # Information from metadata.rb
├── tasks/
│   └── main.yml       # Logic from recipes/default.rb
├── README.md
└── requirements.yml   # External dependencies

roles/
└── cache/
    ├── defaults/
    │   └── main.yml
    ├── meta/
    │   └── main.yml
    ├── tasks/
    │   └── main.yml
    └── README.md
```

### Variable Mapping

Chef attributes will be mapped to Ansible variables:

```yaml
# defaults/main.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Task Mapping

The Chef recipe logic will be mapped to Ansible tasks:

```yaml
# tasks/main.yml
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

### Timeline Estimate

- Analysis and planning: 2 hours
- Migration of cache role: 2 hours
- Migration of simple-nginx role: 4 hours
- Testing and validation: 4 hours
- Documentation: 2 hours

Total estimated time: 14 hours (approximately 2 days)
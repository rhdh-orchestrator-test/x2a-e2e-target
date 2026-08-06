# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with a simple welcome page. The cookbook follows a metadata-only dependency strategy and has both local and external dependencies. The migration scope is relatively small, with only two cookbooks to migrate: the main `simple-nginx` cookbook and its local dependency `cache` cookbook. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, configures it, and creates a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Contains cookbook metadata including name, version, dependencies, and supported platforms. Will need to be translated to Ansible metadata in `meta/main.yml`.
- `attributes/default.rb`: Contains default attributes for Nginx configuration. Will need to be translated to Ansible variables in `defaults/main.yml`.
- `recipes/default.rb`: Contains the main recipe for installing and configuring Nginx. Will need to be translated to Ansible tasks in `tasks/main.yml`.
- `cookbooks/cache/metadata.rb`: Contains metadata for the cache cookbook. Will need to be translated to Ansible metadata in `meta/main.yml` for the cache role.
- `cookbooks/cache/recipes/default.rb`: Contains the recipe for installing and configuring Redis. Will need to be translated to Ansible tasks in `tasks/main.yml` for the cache role.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` module or community.general.nginx role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or credentials were found in the repository
- Standard service security practices should be applied in the Ansible roles:
  - Ensure proper file permissions for Nginx configuration files
  - Configure Redis with authentication if deployed in production

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. In Ansible, dependencies will need to be managed through role requirements or collections.
- **Configuration Management**: Translating Chef attributes to Ansible variables while maintaining the same functionality.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and configuration, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The external `nginx` dependency in the original Chef cookbook is used for advanced Nginx configurations not present in the simple-nginx cookbook itself.
2. No templates or additional configuration files are used beyond what's visible in the repository.
3. No custom resources or libraries are used in the cookbooks.
4. The cookbooks are designed for testing purposes and may require additional hardening for production use.
5. The Redis server installed by the cache cookbook is intended to be used by Nginx for caching, though this integration is not explicitly configured in the visible code.

## Migration Implementation Details

### Ansible Structure

The proposed Ansible structure will consist of:

1. **nginx_role/**
   - `defaults/main.yml` - Variables from attributes/default.rb
   - `tasks/main.yml` - Tasks from recipes/default.rb
   - `meta/main.yml` - Metadata and dependencies

2. **redis_cache_role/**
   - `tasks/main.yml` - Tasks from cookbooks/cache/recipes/default.rb
   - `meta/main.yml` - Metadata from cookbooks/cache/metadata.rb

### Sample Task Translations

**Chef Recipe (recipes/default.rb):**
```ruby
package 'nginx' do
  action :install
end
```

**Ansible Task:**
```yaml
- name: Install nginx
  ansible.builtin.package:
    name: nginx
    state: present
```

**Chef Attribute (attributes/default.rb):**
```ruby
default['nginx']['port'] = 80
```

**Ansible Variable (defaults/main.yml):**
```yaml
nginx_port: 80
```

The migration will be straightforward due to the simplicity of the cookbooks and clear mapping between Chef and Ansible constructs.
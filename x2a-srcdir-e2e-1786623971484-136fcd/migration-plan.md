# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called `simple-nginx` with a local dependency on a `cache` cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration should ensure these dependencies are properly handled in Ansible.
- `attributes/default.rb`: Contains Nginx configuration attributes that need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for installing and configuring Nginx, which needs to be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis, which needs to be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the `supports` statements in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx tasks
- **redis-server (unspecified version)**: Replace with Ansible Galaxy role `geerlingguy.redis` or create custom Redis tasks

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Consider implementing proper security configurations in the Ansible roles:
  - Nginx security best practices (disable unused modules, configure SSL, etc.)
  - Redis security (password protection, network binding, etc.)

### Technical Challenges

- **Dependency Management**: The Chef cookbook uses a metadata-only dependency strategy. Ansible will need to handle dependencies differently, using either Galaxy requirements or including roles directly.
- **Configuration Management**: Convert Chef attributes to Ansible variables, ensuring proper variable precedence.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache

### Assumptions

1. The external 'nginx' dependency mentioned in metadata.rb is not included in the repository and will need to be sourced from Ansible Galaxy or created as a custom role.
2. No complex configurations or templates are used in either cookbook, making the migration relatively straightforward.
3. No custom resources or libraries are used that would require special handling.
4. No secrets management or security configurations are present that would require special attention.
5. The cookbooks are designed for Ubuntu 18.04+ or CentOS 7+ environments.

## Migration Implementation Details

### Ansible Structure

```
ansible/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from simple-nginx/recipes/default.rb
│   │   ├── templates/
│   │   └── defaults/
│   │       └── main.yml  # Converted from simple-nginx/attributes/default.rb
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Converted from cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
├── playbooks/
│   └── site.yml  # Main playbook that includes both roles
└── requirements.yml  # External dependencies
```

### Variable Conversion

Chef attributes from `attributes/default.rb` will be converted to Ansible variables in `roles/nginx/defaults/main.yml`:

```yaml
# Converted from Chef attributes
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

### Task Conversion

The Chef recipe `recipes/default.rb` will be converted to Ansible tasks in `roles/nginx/tasks/main.yml`:

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
    content: '<h1>Welcome to Nginx - Metadata Only Example</h1>'
    dest: /var/www/html/index.html
    mode: '0644'
    owner: root
    group: root
```

Similarly, the cache cookbook will be converted to a Redis role with appropriate tasks.

### Playbook Integration

The main playbook will include both roles:

```yaml
---
- hosts: all
  become: yes
  roles:
    - redis
    - nginx
```

## Testing Strategy

1. Create test VMs matching the supported platforms (Ubuntu 18.04+ and CentOS 7+)
2. Run the Ansible playbooks against these VMs
3. Verify Nginx and Redis are installed and running
4. Verify the welcome page is accessible
5. Compare the results with the original Chef cookbook functionality

## Timeline Estimate

- Analysis and planning: 2 hours
- Role creation and task conversion: 4 hours
- Testing and validation: 4 hours
- Documentation: 2 hours

Total estimated time: 12 hours (1-2 days)
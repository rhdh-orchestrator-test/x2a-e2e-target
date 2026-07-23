# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure focused on deploying Nginx with Redis caching. The migration scope is relatively small, with one main cookbook and one local dependency cookbook. Based on the analysis, this is a straightforward migration that could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a simple welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Basic Nginx installation, service management, static content creation

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server for caching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates a welcome page
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on the 'supports' metadata)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` role or direct package installation using the `apt`/`yum` module
- **cache (1.0.0)**: Migrate the Redis installation to Ansible tasks using the `package` and `service` modules

### Security Considerations

- No explicit security configurations were identified in the current codebase
- No secrets management or credential patterns were detected
- Standard service security should be maintained during migration

### Technical Challenges

- **External dependency**: The 'nginx' cookbook is referenced but not included in the repository. The Ansible migration will need to implement equivalent functionality based on standard Nginx configurations.
- **Attribute mapping**: The Nginx attributes in `attributes/default.rb` will need to be converted to Ansible variables.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Structure Recommendation

```
simple-nginx/
├── defaults/
│   └── main.yml  # Convert Chef attributes to Ansible defaults
├── tasks/
│   └── main.yml  # Convert Chef recipes to Ansible tasks
├── templates/
│   └── index.html.j2  # Convert static content to template
├── meta/
│   └── main.yml  # Define role dependencies
└── README.md
```

### Implementation Details

#### For cache role:
```yaml
# tasks/main.yml
- name: Install Redis server
  package:
    name: redis-server
    state: present

- name: Enable and start Redis service
  service:
    name: redis-server
    enabled: yes
    state: started
```

#### For simple-nginx role:
```yaml
# defaults/main.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto

# tasks/main.yml
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Enable and start nginx service
  service:
    name: nginx
    enabled: yes
    state: started

- name: Create index.html
  template:
    src: index.html.j2
    dest: /var/www/html/index.html
    mode: '0644'
    owner: root
    group: root
```

### Assumptions

1. The external 'nginx' cookbook likely provides more advanced configurations than what's visible in the current repository
2. The Redis configuration is minimal with no custom settings
3. No complex integrations exist between Nginx and Redis beyond basic installation
4. No specific OS-level customizations are required beyond package installation
5. No specific security hardening is implemented in the current cookbooks
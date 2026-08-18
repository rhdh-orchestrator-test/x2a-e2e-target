# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with basic settings. The cookbook has a simple structure with minimal complexity, making it a straightforward migration to Ansible. The estimated timeline for migration is 1-2 days for a single developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs Nginx, ensures the service is running, and creates a basic index page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains default attributes for Nginx configuration (port, user, worker processes)
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates an index page
- `cookbooks/cache/metadata.rb`: Defines cache cookbook metadata
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and starts Redis server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation task
- **cache (local)**: Migrate the Redis installation and service management to Ansible tasks

### Security Considerations

- No explicit security configurations or secrets management identified in the current codebase
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
  - Firewall rules for Redis and Nginx

### Technical Challenges

- **Attribute Management**: Chef attributes need to be converted to Ansible variables
  - Nginx port, user, and worker_processes settings should be defined as variables in Ansible
- **Service Management**: Ensure proper service management in Ansible for both Nginx and Redis

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation and configuration
│   │   └── templates/
│   │       └── index.html.j2  # Template for index page
│   └── redis/
│       └── tasks/
│           └── main.yml  # Redis installation and configuration
└── site.yml  # Main playbook
```

### Migration Steps

1. **Create Ansible Variables**:
   - Convert Chef attributes to Ansible variables in `group_vars/all.yml`:
     ```yaml
     nginx_port: 80
     nginx_user: www-data
     nginx_worker_processes: auto
     ```

2. **Create Redis Role**:
   - Create tasks for Redis installation and service management
   - Example task structure:
     ```yaml
     - name: Install Redis
       package:
         name: redis-server
         state: present
     
     - name: Ensure Redis service is running
       service:
         name: redis-server
         state: started
         enabled: yes
     ```

3. **Create Nginx Role**:
   - Create tasks for Nginx installation, service management, and content creation
   - Example task structure:
     ```yaml
     - name: Install Nginx
       package:
         name: nginx
         state: present
     
     - name: Ensure Nginx service is running
       service:
         name: nginx
         state: started
         enabled: yes
     
     - name: Create index page
       template:
         src: index.html.j2
         dest: /var/www/html/index.html
         mode: '0644'
         owner: root
         group: root
     ```

4. **Create Main Playbook**:
   - Combine roles into a single playbook
   - Example playbook structure:
     ```yaml
     - hosts: all
       roles:
         - redis
         - nginx
     ```

### Assumptions

- The Chef cookbook is used in a simple environment without complex integrations
- No custom configurations for Nginx beyond the basic attributes
- No custom configurations for Redis
- No secrets management or security-specific configurations
- No complex deployment workflows or orchestration
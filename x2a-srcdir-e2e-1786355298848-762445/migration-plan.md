# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef cookbook named `simple-nginx` that installs and configures Nginx with a simple welcome page. The repository is relatively small and straightforward, consisting of one main cookbook and one local dependency cookbook (`cache`). The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for complete migration, testing, and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx with a simple welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe that installs Nginx, starts the service, and creates a welcome page

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation task
- **cache (local)**: Migrate the Redis server installation and configuration to Ansible tasks

### Security Considerations

- No explicit security configurations identified in the current codebase
- No credential patterns detected
- Standard service ports (Nginx on port 80, Redis on default port) should be reviewed for security hardening

### Technical Challenges

- **Attribute Translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables
- **External Dependencies**: The external `nginx` dependency is declared but not included in the repository, requiring investigation of its usage and features

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Main cookbook with Nginx configuration, moderate complexity due to attribute usage

### Assumptions

1. The external `nginx` dependency is used only for basic Nginx installation and configuration, not for complex features
2. No custom templates or additional files are used beyond what's visible in the repository
3. No complex Chef-specific features (data bags, environments, roles) are in use
4. No CI/CD integration or deployment automation is present
5. No secrets management or security hardening is implemented

## Ansible Migration Details

### Proposed Ansible Structure

```
simple-nginx/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Nginx installation and configuration
│   │   └── templates/
│   │       └── index.html.j2  # Welcome page template
│   └── redis/
│       └── tasks/
│           └── main.yml  # Redis installation and configuration
└── site.yml  # Main playbook
```

### Implementation Notes

1. Convert Chef attributes to Ansible variables in `group_vars/all.yml`:
   ```yaml
   nginx_port: 80
   nginx_user: www-data
   nginx_worker_processes: auto
   ```

2. Create Ansible tasks for Nginx installation and configuration:
   ```yaml
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
     template:
       src: index.html.j2
       dest: /var/www/html/index.html
       mode: '0644'
       owner: root
       group: root
   ```

3. Create Ansible tasks for Redis installation and configuration:
   ```yaml
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

4. Create a main playbook that applies both roles:
   ```yaml
   - hosts: all
     roles:
       - redis
       - nginx
   ```

### Testing Strategy

1. Create a test environment with Ubuntu 18.04+ or CentOS 7.0+
2. Run the Ansible playbook against the test environment
3. Verify Nginx and Redis services are running
4. Verify the welcome page is accessible
5. Compare the results with the original Chef cookbook behavior

### Documentation Requirements

1. Document the migration process and decisions
2. Create a README.md for the Ansible repository
3. Document the variables and their usage
4. Include examples for different deployment scenarios
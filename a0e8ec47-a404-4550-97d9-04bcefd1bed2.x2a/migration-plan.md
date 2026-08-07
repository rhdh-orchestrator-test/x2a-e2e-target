# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook called `simple-nginx` and a local dependency cookbook called `cache`. The migration scope is relatively small, with only two cookbooks to migrate. The estimated timeline for migration is 1-2 days given the simplicity of the cookbooks.

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
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role or direct package installation using the `apt` or `yum` module
- **cache (local)**: Migrate to Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were found in the cookbooks
- No secrets management or credential patterns were detected
- Standard service security should be maintained during migration

### Technical Challenges

- **Dependency Management**: The main cookbook depends on both a local cookbook (cache) and an external cookbook (nginx). In Ansible, this would be handled through role dependencies or include_role/import_role.
- **Attribute Translation**: Chef attributes need to be converted to Ansible variables, particularly the Nginx configuration attributes.

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Ansible Migration Details

#### 1. Directory Structure

Create the following Ansible structure:

```
ansible-migration/
├── inventory/
│   └── hosts
├── group_vars/
│   └── all.yml
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── templates/
│   │       └── index.html.j2
│   └── redis/
│       ├── tasks/
│       │   └── main.yml
│       └── handlers/
│           └── main.yml
└── site.yml
```

#### 2. Variable Mapping

Chef attributes to Ansible variables:

```yaml
# group_vars/all.yml
nginx_port: 80
nginx_user: www-data
nginx_worker_processes: auto
```

#### 3. Role Development

**nginx role**:
- Install nginx package
- Configure service to be enabled and started
- Create index.html file with welcome message

**redis role**:
- Install redis-server package
- Configure service to be enabled and started

#### 4. Playbook Development

Create a main playbook that applies both roles as needed.

### Assumptions

- The Chef cookbooks are used in a standard Chef environment
- No custom resources or libraries are being used
- No complex configuration management beyond what's visible in the recipes
- No special handling for different operating systems beyond the basic package names
- No special security requirements or hardening is needed
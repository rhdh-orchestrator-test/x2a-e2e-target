# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef cookbook called "simple-nginx" that needs to be migrated to Ansible. The cookbook is relatively simple, focusing on installing and configuring Nginx with a basic welcome page. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for complete migration, testing, and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Main cookbook that installs and configures Nginx web server with a basic welcome page
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Local dependency cookbook that installs and configures Redis as a caching server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible metadata or requirements files.
- `attributes/default.rb`: Contains configuration attributes for Nginx including port, user, and worker processes. Will need to be migrated to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a basic index page. Will need to be migrated to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. Will need to be migrated to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (based on the `supports` statements in metadata.rb)
- **Virtual Machine Technology**: Not specified in the repository
- **Cloud Platform**: Not specified in the repository

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **cache (local)**: Migrate the Redis installation and configuration to an Ansible role or include task

### Security Considerations

- No explicit security configurations were found in the repository
- No secrets management or vault usage was detected
- Consider implementing TLS/SSL for Nginx in the Ansible role
- Implement proper file permissions for the web content

### Technical Challenges

- **Attribute Translation**: Chef attributes need to be converted to Ansible variables with appropriate defaults
- **Service Management**: Ensure proper service management across different OS platforms
- **External Dependencies**: The external nginx dependency needs to be replaced with an appropriate Ansible solution

### Migration Order

1. **cache role/tasks** (Priority 1): Simple Redis installation and service management
2. **simple-nginx role** (Priority 2): Main Nginx installation and configuration

### Assumptions

1. The cookbook is used in a simple environment without complex integrations
2. The external nginx dependency is used for additional Nginx configurations not present in this repository
3. No custom templates or additional files are used beyond what's visible in the repository
4. No complex conditionals or platform-specific code is present
5. No secrets management or security hardening is implemented
6. The cookbook is designed for testing purposes as indicated in the README.md

## Ansible Structure Recommendation

```
ansible-simple-nginx/
├── inventory/
│   └── hosts.ini
├── group_vars/
│   └── all.yml  # Variables converted from attributes/default.rb
├── roles/
│   ├── nginx/
│   │   ├── defaults/
│   │   │   └── main.yml  # Default variables
│   │   ├── tasks/
│   │   │   └── main.yml  # Installation and configuration tasks
│   │   └── templates/
│   │       └── index.html.j2  # Template for welcome page
│   └── redis/
│       ├── defaults/
│       │   └── main.yml
│       └── tasks/
│           └── main.yml  # Redis installation and service tasks
├── playbook.yml  # Main playbook that includes both roles
└── requirements.yml  # External role dependencies
```

## Migration Timeline

- **Analysis and Planning**: 1 day (completed)
- **Role Development**: 2-3 days
- **Testing**: 2-3 days
- **Documentation**: 1 day
- **Knowledge Transfer**: 1 day
- **Total**: 7-9 days (1-2 weeks)
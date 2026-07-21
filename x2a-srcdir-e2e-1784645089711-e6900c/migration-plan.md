# MIGRATION FROM CHEF TO ANSIBLE

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains a simple Chef cookbook structure with a main cookbook (simple-nginx) and a local dependency cookbook (cache).

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation and configuration cookbook that creates a basic web server with a welcome page
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content deployment

- **cache**:
    - Description: Redis cache server installation and configuration for providing caching functionality
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

**CRITICAL PATH VERIFICATION:**
- Verified path `recipes/default.rb` exists for simple-nginx cookbook using `list_directory(dir_path=recipes)` which returned `default.rb`
- Verified path `cookbooks/cache/recipes/default.rb` exists for cache cookbook using `list_directory(dir_path=cookbooks/cache/recipes)` which returned `default.rb`
- Searched for additional Chef cookbooks using `file_search(pattern="**/recipes/default.rb")`, `file_search(pattern="recipes/*.rb")`, and `file_search(pattern="**/*.rb")` - no additional modules found
- Searched for Puppet modules using `file_search(pattern="**/manifests/init.pp")` - no Puppet modules found
- Searched for PowerShell modules using `file_search(pattern="**/*.psd1")` - no PowerShell modules found

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for installing and configuring Nginx
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (explicitly supported in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **cache (1.0.0)**: Local dependency that installs Redis, replace with Ansible Redis role or community.general.redis module

### Security Considerations

- No explicit security configurations identified in the current codebase
- Vault/secrets management:
  - No credentials detected in the repository
  - No encrypted data bags or Chef Vault usage identified
  - No SSL/TLS certificate references found

### Technical Challenges

- **Attribute Translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables
- **Dependency Management**: External dependency on 'nginx' cookbook needs to be replaced with appropriate Ansible role or modules
- **Service Management**: Ensure proper service management for both Nginx and Redis services

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation and service management, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation and configuration, depends on cache cookbook

### Assumptions

1. The repository is a simple example and may not represent the full production environment
2. No complex Chef features (data bags, environments, roles) are being used
3. No custom resources or libraries are present
4. The external 'nginx' dependency is a standard community cookbook
5. No complex configuration templates are being used
6. No authentication or authorization mechanisms are implemented
7. No specific performance tuning or optimization is required
8. No backup or disaster recovery processes are defined
9. No monitoring or logging configurations are present
10. No specific network configurations or firewall rules are defined

## Migration Timeline Estimate

Given the simplicity of the cookbooks:

- **Analysis and Planning**: 1 day
- **Development of Ansible Roles**:
  - cache role: 1 day
  - nginx role: 2 days
- **Testing**: 2 days
- **Documentation**: 1 day
- **Deployment**: 1 day

**Total Estimated Timeline**: 1 week

## Ansible Structure Recommendation

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml  # Variables converted from Chef attributes
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │   │   └── main.yml  # Converted from recipes/default.rb
│   │   ├── templates/
│   │   │   └── index.html.j2  # Converted from file resource
│   │   └── defaults/
│   │       └── main.yml  # Converted from attributes/default.rb
│   └── redis/
│       ├── tasks/
│       │   └── main.yml  # Converted from cookbooks/cache/recipes/default.rb
│       └── defaults/
│           └── main.yml
└── site.yml  # Main playbook
```
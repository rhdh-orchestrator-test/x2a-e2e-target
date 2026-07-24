# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a simple Chef cookbook structure with a main cookbook (simple-nginx) and a local dependency cookbook (cache). The migration to Ansible is relatively straightforward due to the limited scope and simple functionality of the cookbooks.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx web server installation and configuration
    - Path: ./ (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation and configuration as a caching layer
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration consideration: Convert dependencies to Ansible roles or collections.
- `attributes/default.rb`: Contains configuration attributes for nginx. Migration consideration: Convert to Ansible variables.
- `recipes/default.rb`: Main recipe for installing and configuring nginx. Migration consideration: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for cache cookbook. Migration consideration: Convert to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for installing and configuring Redis. Migration consideration: Convert to Ansible tasks.

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: The cookbooks support Ubuntu 18.04+ and CentOS 7.0+ as specified in the metadata.rb files.
- **Virtual Machine Technology**: Not specified in the repository.
- **Cloud Platform**: No cloud-specific configurations found.

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible community.general.nginx or install via package module
- **redis-server (unspecified version)**: Replace with Ansible community.general.redis or install via package module

### Security Considerations

- No explicit security configurations found in the cookbooks.
- No secrets management or credential patterns detected.
- Basic file permissions are set for the index.html file (mode '0644').

### Technical Challenges

- **Dependency Management**: The main cookbook depends on an external 'nginx' cookbook that is not included in the repository. The Ansible migration will need to implement the functionality directly or use an appropriate Ansible Galaxy role.
- **Configuration Management**: The nginx attributes need to be converted to Ansible variables with appropriate defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Low complexity, standalone Redis installation and service management.
2. **simple-nginx cookbook** (Priority 2): Depends on cache, implements basic nginx installation and configuration.

### Assumptions

1. The external 'nginx' dependency is used only for installation and basic configuration, as the cookbook implements its own nginx configuration.
2. No complex templating or configuration is required beyond what's visible in the repository.
3. No custom resources or libraries are used in the cookbooks.
4. No secrets management or security-specific configurations are needed.
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+.

## Migration Timeline Estimate

Given the simplicity of the cookbooks, the migration should be relatively quick:

1. **Analysis and Planning**: 1 day (completed)
2. **Development of Ansible Roles**:
   - cache role: 0.5 day
   - simple-nginx role: 1 day
3. **Testing**: 1 day
4. **Documentation and Knowledge Transfer**: 0.5 day

**Total Estimated Timeline**: 3-4 days

## Ansible Structure Recommendation

```
ansible-nginx/
├── inventories/
│   └── production/
│       ├── hosts
│       └── group_vars/
│           └── all.yml  # Variables from attributes/default.rb
├── roles/
│   ├── cache/
│   │   ├── meta/
│   │   │   └── main.yml  # From cookbooks/cache/metadata.rb
│   │   └── tasks/
│   │       └── main.yml  # From cookbooks/cache/recipes/default.rb
│   └── nginx/
│       ├── meta/
│       │   └── main.yml  # From metadata.rb
│       └── tasks/
│           └── main.yml  # From recipes/default.rb
├── playbooks/
│   └── site.yml  # Main playbook that includes both roles
└── README.md
```

## Migration Steps

1. Create Ansible roles structure as outlined above
2. Convert Chef resources to Ansible modules:
   - `package` resources → `ansible.builtin.package` or specific modules like `apt` or `yum`
   - `service` resources → `ansible.builtin.service`
   - `file` resources → `ansible.builtin.file` or `ansible.builtin.copy`
3. Convert Chef attributes to Ansible variables in group_vars or role defaults
4. Create a main playbook that applies the roles in the correct order
5. Test the playbook against target environments
6. Document the new Ansible structure and usage
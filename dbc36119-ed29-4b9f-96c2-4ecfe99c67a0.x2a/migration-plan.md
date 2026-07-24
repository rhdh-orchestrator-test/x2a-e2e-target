# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure with a main cookbook (simple-nginx) and one local dependency cookbook (cache). The migration scope is relatively small, with two cookbooks that handle basic nginx web server and Redis cache server installation and configuration. Based on the repository size and complexity, this migration is estimated to be low complexity and could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple nginx cookbook for testing metadata-only dependency strategy
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook - local dependency for testing
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation and service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx'. Migration considerations: Dependencies will need to be handled through Ansible roles or collections.
- `attributes/default.rb`: Contains default attributes for nginx configuration. Migration considerations: These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe for nginx installation and configuration. Migration considerations: Convert to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook. Migration considerations: Will need to be converted to Ansible role metadata.
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis installation and service management. Migration considerations: Convert to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (explicitly specified in metadata.rb)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (unspecified version)**: Replace with Ansible's `nginx` module or community.general collection
- **redis-server (unspecified version)**: Replace with Ansible's `apt`/`yum` modules for installation and `systemd` module for service management

### Security Considerations

- No explicit security configurations were identified in the cookbooks
- No secrets management or credential patterns were detected
- Basic service configuration should maintain default security settings

### Technical Challenges

- **Dependency Management**: The main cookbook depends on both a local cookbook (cache) and an external cookbook (nginx). In Ansible, this would be handled through role dependencies or collections.
  - Mitigation: Create separate Ansible roles for each cookbook and define dependencies in the role metadata.

- **Platform Support**: The cookbooks support both Ubuntu and CentOS. Ansible playbooks will need to handle platform-specific differences.
  - Mitigation: Use Ansible's built-in facts and conditionals to handle platform-specific tasks.

### Migration Order

1. **cache role** (Priority 1): Simple Redis installation and service management, no dependencies
2. **nginx role** (Priority 2): Depends on cache role, handles nginx installation and configuration

### Assumptions

1. The nginx cookbook dependency is an external dependency not included in the repository
2. No complex configuration templates are used for nginx or Redis
3. No custom resources or libraries are used in the cookbooks
4. No secrets management or credential handling is required
5. The cookbooks are designed for testing purposes and may not represent production-ready configurations
6. The nginx configuration uses the default attributes defined in attributes/default.rb

## Migration Steps

1. Create an Ansible role structure for each cookbook
2. Convert Chef attributes to Ansible variables
3. Convert Chef recipes to Ansible tasks
4. Create role dependencies to mirror cookbook dependencies
5. Create a main playbook that includes both roles
6. Test the playbook on supported platforms (Ubuntu 18.04+ and CentOS 7.0+)
7. Document the migration process and any platform-specific considerations

## Timeline Estimate

- Analysis and planning: 2 hours
- Role creation and task conversion: 4 hours
- Testing and validation: 2 hours
- Documentation: 2 hours

Total estimated time: 10 hours (1-2 days)
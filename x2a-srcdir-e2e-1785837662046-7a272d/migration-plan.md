# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook structure for Nginx installation with a local dependency on a Redis cache cookbook. The migration scope is relatively small, consisting of two Chef cookbooks with straightforward functionality. Based on the limited complexity, this migration could be completed within 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx web server installation with basic configuration
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx package installation, service management, basic HTML content

- **cache**:
    - Description: Redis server installation for caching functionality
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis package installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies on 'cache' and 'nginx' cookbooks
- `attributes/default.rb`: Contains configuration attributes for Nginx (port, user, worker processes)
- `recipes/default.rb`: Main recipe for Nginx installation and configuration
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook
- `cookbooks/cache/recipes/default.rb`: Recipe for Redis server installation and service management

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7.0+ (as specified in metadata.rb support declarations)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible nginx role from Ansible Galaxy or create a custom role
- **cache (local)**: Migrate to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations or credentials were found in the examined files
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
  - Network access controls

### Technical Challenges

- **Attribute Translation**: Chef attributes in `attributes/default.rb` need to be converted to Ansible variables
  - Solution: Create corresponding variables in Ansible role defaults/main.yml

- **External Dependencies**: The external 'nginx' cookbook dependency needs to be replaced
  - Solution: Either use community.general.nginx_module or create a custom Ansible role for Nginx

### Migration Order

1. **cache cookbook** (Priority 1): Simple Redis installation, low complexity
2. **simple-nginx cookbook** (Priority 2): Nginx installation with basic configuration

### Assumptions

1. The external 'nginx' cookbook is used only for its declared dependency and not directly referenced in the code
2. No complex Chef-specific features (e.g., data bags, environments, roles) are in use
3. No custom templates or additional configuration files exist beyond what was discovered
4. No specific security hardening or customization is required beyond basic installation
5. The target environment will continue to be Ubuntu 18.04+ or CentOS 7.0+
6. No integration with external services or monitoring systems is required
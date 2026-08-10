# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a simple Chef cookbook called "simple-nginx" that installs and configures Nginx with basic settings. The migration scope is relatively small, consisting of one main cookbook with a local dependency on a "cache" cookbook that installs Redis. The estimated timeline for migration is 1-2 days given the limited complexity and small codebase.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Simple Nginx cookbook that installs and configures Nginx web server with basic settings
    - Path: / (root directory)
    - Technology: Chef
    - Key Features: Nginx installation, service management, basic HTML content creation

- **cache**:
    - Description: Simple cache cookbook that installs and configures Redis server
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis server installation, service management

### Infrastructure Files

- `metadata.rb`: Defines cookbook metadata including dependencies, version, and supported platforms. Will need to be translated to Ansible role metadata.
- `attributes/default.rb`: Contains default Nginx configuration attributes. These will need to be converted to Ansible variables.
- `recipes/default.rb`: Main recipe that installs Nginx, ensures the service is running, and creates a simple index page. Will be converted to Ansible tasks.
- `cookbooks/cache/metadata.rb`: Metadata for the cache cookbook.
- `cookbooks/cache/recipes/default.rb`: Recipe that installs and configures Redis server. Will be converted to Ansible tasks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (as specified in metadata.rb supports statements)
- **Virtual Machine Technology**: Not specified
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (external)**: Replace with Ansible's `nginx` role or direct package installation using the `apt` or `yum` module
- **cache (local)**: Convert to an Ansible role for Redis installation and configuration

### Security Considerations

- No explicit security configurations were identified in the codebase
- No secrets management or credential patterns were detected
- Standard service security practices should be applied in the Ansible roles:
  - Proper file permissions for configuration files
  - Service user restrictions
  - Network access controls for Redis

### Technical Challenges

- **Simple Conversion**: The cookbook is straightforward with minimal complexity, making it a good candidate for direct translation to Ansible roles
- **Dependency Management**: The external nginx dependency will need to be replaced with appropriate Ansible modules or roles
- **Platform Support**: Ensure the Ansible roles maintain support for both Ubuntu and CentOS as specified in the original cookbooks

### Migration Order

1. **cache cookbook** (Priority 1): Convert to an Ansible role first as it's a dependency for the main cookbook
2. **simple-nginx cookbook** (Priority 2): Convert to an Ansible role after the cache role is completed

### Assumptions

1. The cookbook is used in a simple environment without complex integrations
2. No custom templates or additional files beyond what's visible in the repository
3. No complex configuration management beyond the basic attributes defined
4. No orchestration or ordering dependencies with other systems
5. No secrets or sensitive data management requirements
6. The external nginx dependency uses standard configurations that can be easily replicated in Ansible

## Migration Steps

1. Create an Ansible role structure for both components:
   ```
   roles/
     nginx/
       defaults/
         main.yml  # Convert attributes/default.rb here
       tasks/
         main.yml  # Convert recipes/default.rb here
       meta/
         main.yml  # Convert metadata.rb here
     redis/
       tasks/
         main.yml  # Convert cookbooks/cache/recipes/default.rb here
       meta/
         main.yml  # Convert cookbooks/cache/metadata.rb here
   ```

2. Convert Chef resources to Ansible modules:
   - `package` resources → Ansible `apt`/`yum` modules
   - `service` resources → Ansible `service` module
   - `file` resources → Ansible `file` or `copy` modules

3. Convert Chef attributes to Ansible variables in `defaults/main.yml`

4. Create a main playbook that includes both roles with appropriate ordering

5. Test the migration on supported platforms (Ubuntu 18.04+ and CentOS 7+)

6. Document the new Ansible structure and usage instructions
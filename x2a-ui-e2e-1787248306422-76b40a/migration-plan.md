# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation. It also contains scripts for setting up Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and their straightforward nature.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles that perform the same checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform
  - Ansible Tower/AWX for web UI, job scheduling, and inventory management
  - Ansible Galaxy for role sharing and distribution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migrated Ansible roles:
  - Continue to enforce TLSv1.2 or higher
  - Disable vulnerable protocols
  - Generate proper self-signed certificates or integrate with Let's Encrypt

- **SSH Hardening**: The InSpec tests verify SSH security. Ensure the migrated solution:
  - Continues to enforce SSH best practices
  - Disables root login
  - Maintains compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the modules

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests, and consider using the ansible.builtin.uri module for HTTP/HTTPS checks

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible roles
  - Mitigation: Create Ansible roles that install and configure Ansible Automation Platform components instead of Chef components

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Simply review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure with defaults, tasks, handlers, etc.

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Consider merging with the website_https role as a security enhancement

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible assertions or a separate security role

4. **Chef Server Deployment Scripts** (high complexity)
   - Replace with Ansible roles for deploying Ansible Automation Platform
   - Create roles for configuring users, organizations, and projects in Ansible Tower/AWX

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The InSpec tests are used for compliance verification rather than traditional unit/integration testing
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
4. The deployment scripts are intended for on-premises or generic cloud VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The migration will replace Chef components with Ansible equivalents while maintaining the same functionality
7. No specific performance requirements are mentioned, so standard Ansible practices should suffice
8. No specific security requirements beyond what's in the InSpec tests
9. No specific backup or disaster recovery requirements
10. The migration will not require changes to the underlying infrastructure or application architecture
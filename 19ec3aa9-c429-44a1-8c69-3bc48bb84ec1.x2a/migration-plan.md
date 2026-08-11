# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef infrastructure setup scripts that need to be migrated to a unified Ansible approach. The repository appears to be primarily focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, rather than containing traditional Chef cookbooks. The migration scope is relatively small, with only a few Ansible playbooks and Chef infrastructure setup scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef infrastructure scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **InSpec Tests**: Convert to Ansible-native testing with Molecule and testinfra, or maintain InSpec tests as a separate compliance layer
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX for centralized automation management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. This security check should be incorporated into the Ansible migration.
- **Credentials Management**: The Chef server setup scripts contain hardcoded credentials that should be moved to Ansible Vault or another secure credential management solution:
  - Username/password for Chef user creation
  - Organization name and details
  - Count: 5 credentials detected in setup scripts (hostname, username, useremail, userpassword, orgname)

### Technical Challenges

- **InSpec Integration**: The repository demonstrates using InSpec with Ansible for compliance testing. The migration should maintain this compliance testing capability, either by continuing to use InSpec or by migrating to an Ansible-native solution.
- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible roles that can deploy alternative configuration management or compliance tools if needed.

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
2. **poodle-fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires decision on testing strategy)
4. **Chef server deployment scripts** (high complexity, requires architectural decisions)

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, replacing Chef components.
2. The InSpec compliance testing functionality is still desired, either through continued use of InSpec or migration to an Ansible-native solution.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up infrastructure that will be replaced by Ansible Automation Platform or similar.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain or improve the security posture demonstrated in the existing code.
6. No actual Chef cookbooks exist in the repository, only Chef infrastructure setup scripts and InSpec tests.
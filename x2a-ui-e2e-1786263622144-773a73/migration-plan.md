# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef automation scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with some Chef server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality. Will need to be converted to Ansible-compatible test format.
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Will need to be converted to Ansible-compatible test format.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or Ansible Test
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Chef Automate/Server**: Determine if Chef Automate functionality needs to be replicated in Ansible environment or if it can be replaced with alternatives like AWX/Tower

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in migrated Ansible roles.
- **SSH Security**: The InSpec profile checks for SSH root login security. Ensure this security check is implemented in the Ansible roles.
- **Credentials Management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates in website_https.yml
  - Consider using Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Tests Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require additional effort.
- **Chef Server Deployment**: Determining whether to replace Chef Server deployment scripts with Ansible AWX/Tower deployment or other configuration management solution.

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Implement proper variable management
   - Add documentation

2. **poodle_fix.yml** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Implement proper variable management
   - Add documentation

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure all compliance checks are maintained

4. **Chef Server Deployment Scripts** (high complexity)
   - Determine replacement strategy
   - Implement Ansible playbooks for equivalent functionality if needed

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. The InSpec tests are valuable and need to be preserved in some form
3. The Chef Automate/Server deployment scripts may be replaced with Ansible AWX/Tower or other alternatives
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The current Ansible playbooks are functional and can be used as a reference for the migration
6. No external dependencies or integrations beyond what's visible in the repository
7. The repository is primarily for demonstration purposes and may not represent production-grade configurations
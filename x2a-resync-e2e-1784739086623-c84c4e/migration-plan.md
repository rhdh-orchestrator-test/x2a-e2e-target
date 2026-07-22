# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

After thorough examination of the repository using file_search for patterns "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found. The repository contains:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests for SSH root login configuration, STIG compliance checks

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Likely a static file used by the website_https playbook
- `README.md`: Repository documentation indicating this is a collection of Chef examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Replace with Ansible-compatible testing frameworks like Molecule with Testinfra or ansible-test
- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks for equivalent functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure continued disabling of SSLv3 (POODLE vulnerability mitigation)
  - Enforce TLSv1.2 or higher
  - Maintain proper certificate generation and management

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure root login remains disabled
  - Maintain SSH security controls during migration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Replace with Ansible Vault for secure credential storage
  - Count of credentials detected: 4 (username, longusername, useremail, userpassword) in each deployment script

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Solution: Use Molecule with Testinfra or ansible-test for similar functionality
  - Ensure all current test coverage is maintained

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible:
  - Solution: Create Ansible roles for Chef Server deployment or consider if Chef Server is still needed
  - If Chef Server is no longer needed, document alternative approaches

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, already in Ansible format
   - Refactor into proper Ansible roles and structure
   - Update to use Ansible best practices (variables, handlers, etc.)

2. **Testing Framework**:
   - Convert InSpec tests to Molecule/Testinfra
   - Ensure all security checks are maintained

3. **Chef Server Deployment**:
   - Highest complexity
   - Create Ansible playbooks to replace Chef Automate/Server deployment scripts
   - Or document alternative approaches if Chef Server is no longer needed

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Ansible playbooks are already functional and may only need structural improvements rather than functional changes.

3. The Chef InSpec tests are used for compliance verification and will need equivalent functionality in the Ansible ecosystem.

4. The Chef Automate and Chef Server deployment scripts may or may not be needed in the final Ansible implementation, depending on whether Chef infrastructure is still required.

5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will need to be replaced with secure credential management in the production implementation.

6. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be flexible enough to work in other environments.

7. No traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository, despite thorough searching with appropriate patterns.
# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts that need to be migrated to a standardized Ansible approach. After thorough analysis using file_search for Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), and PowerShell modules (.psd1), no traditional infrastructure-as-code modules were found.

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on test conversion and validation.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

Based on thorough repository analysis using file_search for the patterns **/manifests/init.pp, **/recipes/default.rb, and **/*.psd1, no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository.

The file_search results confirm:
- No Puppet modules with manifests/init.pp
- No Chef cookbooks with recipes/default.rb
- No PowerShell modules with .psd1 manifests

The repository instead contains the following components that require migration:

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh-compliance**:
    - Description: Chef InSpec profile for validating SSH configuration compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards

- **website-https-verification**:
    - Description: Chef InSpec profile for validating HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response testing, SSL protocol validation

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Simple HTML file used for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis and best practices validation

- **Test Kitchen (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule for Ansible role and playbook testing
  - Option 2: Create simple Vagrant-based testing scripts using Ansible directly

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Use GitLab CI/CD or Jenkins with Ansible for automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec tests validate SSH root login restrictions.
  - Migration approach: Create an Ansible playbook that implements the same SSH hardening measures and use Ansible's assert module to validate the configuration

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded usernames and passwords
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible modules, and implement equivalent tests using Ansible's assert module or Molecule verify phase

- **Chef Server Replacement**: The Chef Server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation strategy: Evaluate if Chef Server functionality is still needed; if so, create Ansible playbooks to deploy and configure an alternative configuration management solution or use AWX/Ansible Tower

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Add documentation and variable descriptions

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Consider merging with the website-https playbook for a comprehensive web server configuration

3. **InSpec tests** (moderate complexity)
   - Convert the website-https-verify.rb tests to Ansible assertions or Molecule tests
   - Convert the ssh_profile.rb tests to Ansible assertions or Molecule tests

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement secure credential handling using Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than to provide production-ready configurations
2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration purposes
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The security configurations (SSL, SSH) are minimal examples and would need enhancement for production use
5. There is no existing Ansible inventory or host configuration in the repository
6. The repository does not contain actual Chef cookbooks or recipes that need migration
7. The Test Kitchen configuration is used primarily for testing the Ansible playbooks with InSpec verification
8. The migration will standardize on Ansible-native tools and approaches rather than maintaining hybrid tooling
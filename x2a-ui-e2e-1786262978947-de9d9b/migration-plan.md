# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used as a template for the web server. Can be directly incorporated into Ansible playbooks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Ansible Tower for enterprise automation
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The current playbooks properly configure TLSv1.2 and disable SSLv3. This security practice should be maintained in the migrated Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. This check should be incorporated into the Ansible playbooks using the `assert` module or as a separate compliance role.

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, but in production environments, consider using ansible-vault for storing sensitive certificate data
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible playbooks will require understanding of Chef Server architecture.
  - Mitigation: Create an Ansible role that installs and configures AWX/Tower as a replacement for Chef Server functionality

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Add idempotency checks and improve variable usage

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Review and potentially merge with the website_https playbook as a role

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to deploy alternative automation platform (AWX/Tower)
   - Ensure user/organization management is handled appropriately

### Assumptions

1. The current setup uses Test Kitchen primarily for testing Ansible playbooks, not for testing Chef cookbooks.
2. The InSpec tests are used for compliance verification of infrastructure deployed by Ansible.
3. The deployment scripts are used for setting up a Chef environment, which will be replaced by an Ansible-based automation platform.
4. The target environment is Ubuntu 20.04, but the playbooks should be made more flexible to support other distributions.
5. The current implementation uses self-signed certificates for development/testing purposes. Production environments would require proper certificate management.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks focused on demonstrating compliance automation. The repository is relatively small and appears to be primarily for demonstration purposes rather than a full production infrastructure.

After thorough analysis using file_search for Puppet modules (`**/manifests/init.pp`), Chef cookbooks (`**/recipes/default.rb`), and PowerShell modules (`**/*.psd1`), no traditional infrastructure-as-code modules were found. The repository contains Ansible playbooks, Chef InSpec tests, and shell scripts for deploying Chef Automate and Chef Infra Server.

The migration complexity is low, with an estimated timeline of 1 week for a complete migration. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains components that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified all paths using `list_directory` and `file_search` commands. The file_search commands for `**/manifests/init.pp` (Puppet), `**/recipes/default.rb` (Chef), and `**/*.psd1` (PowerShell) returned no results, confirming no traditional infrastructure-as-code modules exist in this repository.

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test for verifying HTTPS configuration and TLS settings
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for more comprehensive testing
  - Option 4: Consider migrating to ansible-compliance if maintaining InSpec-like capabilities is important

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Consider using Molecule's Vagrant driver to maintain similar local testing capabilities

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for similar enterprise capabilities

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable vulnerable protocols. This security hardening must be preserved in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This compliance check must be preserved.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule tests

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbook

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing mechanisms while maintaining the same level of compliance verification.
  - Mitigation: Use a combination of Ansible assert modules and Molecule tests to replicate InSpec functionality

- **Test Kitchen Integration**: Replacing Test Kitchen with Ansible-native testing tools.
  - Mitigation: Use Molecule with Vagrant driver to provide similar functionality

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting, finding an equivalent in the Ansible ecosystem.
  - Mitigation: Consider Ansible Tower/AWX with compliance scanning capabilities or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (low risk, already in Ansible): Review and optimize the existing Ansible playbooks
   - chef-and-ansible/website_https.yml
   - chef-and-ansible/poodle_fix.yml

2. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing mechanisms
   - chef-and-ansible/tests/website_https_verify.rb
   - chef-and-ansible/tests/ssh_profile.rb

3. **Chef Deployment Scripts** (high complexity): Create Ansible playbooks to replace the bash scripts for Chef deployment
   - setup-automate/deploy-automate.sh
   - setup-automate/deploy-chef-server.sh

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. The InSpec compliance testing functionality needs to be preserved
3. The deployment scripts for Chef Automate/Infra Server may be replaced with equivalent infrastructure deployment using Ansible
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external data sources or complex integrations are present in the current implementation
6. The repository is primarily for demonstration purposes rather than production use
7. No complex state management or database configurations are present
8. No custom Chef resources or complex Ruby code needs to be migrated
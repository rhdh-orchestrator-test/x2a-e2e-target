# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used together for compliance automation. The primary technology is Ansible for configuration management with Chef InSpec for compliance testing. There are also Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on standardizing all components to Ansible while preserving the compliance testing capabilities.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The Ansible playbooks can be directly reused, while the InSpec tests need to be converted to Ansible equivalents.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests SSH root login configuration, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the website. Can be directly reused in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Integrate with other compliance tools like Ansible Lint or OpenSCAP

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solutions:
  - Option 1: Ansible Tower/AWX for enterprise management
  - Option 2: Ansible Semaphore for lightweight management
  - Option 3: GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Directly reuse the existing Ansible SSL configuration tasks

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create equivalent Ansible assert tasks or custom modules to perform the same compliance checks

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management solution
  - Mitigation: Document manual setup steps for Ansible Tower/AWX or create Ansible playbooks to deploy the chosen management solution

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, direct reuse with minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible testing framework
3. **Chef Server Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires replacement with Ansible management solution

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. Compliance testing is still a requirement after migration
3. The existing Ansible playbooks are working correctly and can be directly reused
4. The target environment will remain Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The hardcoded credentials in setup scripts are for testing only and will be replaced with secure alternatives
7. The self-signed certificates are for testing only and will be replaced with proper certificates in production
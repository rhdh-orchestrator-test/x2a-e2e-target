# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec testing components that need to be migrated to a unified Ansible solution. The repository demonstrates Chef InSpec for compliance testing with Ansible deployments, along with Chef Automate and Chef Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and Chef deployment scripts to convert. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related components that need individual migration planning:

### MODULE INVENTORY

Based on thorough file searches (`**/manifests/init.pp`, `**/recipes/default.rb`, and `**/*.psd1`), no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository.

The repository contains the following components to migrate:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
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
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Ansible Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - Consider OpenSCAP or DISA STIG Ansible roles for compliance testing

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform (formerly Ansible Tower) for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper idempotency checks
  
- **SSH Hardening**: The InSpec tests check for SSH root login restrictions
  - Approach: Implement an Ansible role for SSH hardening that applies the same security controls
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Use Ansible's crypto modules to generate certificates or consider integrating with Let's Encrypt

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible assert modules or molecule verify phase with custom verification scripts
  
- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible management
  - Mitigation: Implement Ansible roles for configuration management that achieve the same functionality

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Convert to proper Ansible role structure
   - Add idempotency checks
   - Implement variable substitution for better reusability

2. **poodle_fix.yml** (low risk, already Ansible)
   - Convert to proper Ansible role structure
   - Add idempotency checks
   - Combine with website_https role as an optional security enhancement

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible Molecule tests
   - Implement equivalent assertions

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential storage
   - Consider containerization options for Chef components if still needed

### Assumptions

1. The primary goal is to migrate all automation to Ansible, not to maintain Chef InSpec integration
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The Chef Automate and Chef Server deployments are needed in the new Ansible automation
5. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives
6. The SSL and Apache configurations are representative of actual production needs
7. The InSpec tests represent actual compliance requirements that must be maintained
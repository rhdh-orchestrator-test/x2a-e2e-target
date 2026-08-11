# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for Apache SSL configuration
  - Ensure TLSv1.2 is enabled and older protocols are disabled
  - Maintain self-signed certificate generation process
  
- **SSH Hardening**: Maintain SSH security controls that disable root login
  - Convert InSpec SSH profile tests to Ansible security role or include in playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing framework
  - Mitigation: Use Ansible's assert module or Molecule for testing, or maintain InSpec as a separate testing tool
  
- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Evaluate Ansible Automation Platform or AWX as replacements for Chef Automate's functionality

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production infrastructure codebase
2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration purposes
3. The hardcoded credentials in the deployment scripts are not used in production environments
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The migration will maintain the same level of security compliance testing currently provided by InSpec
6. The Apache web server configuration requirements will remain the same in the migrated solution
# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL protocol verification, SSH root login security check

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate deployment, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Maintain InSpec as a separate compliance tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Custom Ansible playbooks for test environment provisioning

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH root login restrictions verified by the InSpec tests
  - Ensure the Ansible equivalent maintains the same security posture

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use ansible.builtin.assert or ansible.builtin.uri modules to perform similar checks
  - Consider maintaining InSpec for compliance testing if direct conversion is too complex

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow
  - Mitigation: Implement Molecule testing framework for Ansible roles

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https role as a security enhancement

3. **compliance-tests** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Alternatively, maintain InSpec tests but integrate with Ansible workflow

4. **chef-deployment scripts** (high complexity)
   - Convert shell scripts to Ansible roles for deploying monitoring/compliance tools
   - Replace Chef Automate functionality with alternative compliance solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (SSL protocols, SSH configuration) must be maintained in the migrated solution
5. The Chef Automate and Chef Server deployment may be replaced with alternative compliance monitoring solutions
6. No external dependencies or integrations beyond what's visible in the repository
7. No specific performance requirements for the deployed applications
8. No specific backup or disaster recovery requirements
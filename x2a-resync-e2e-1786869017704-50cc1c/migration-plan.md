# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with a focus on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec profiles for compliance testing
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG references

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deployment**:
    - Description: Shell script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom test modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec as a standalone testing tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance platforms like Ansible Automation Platform
  - Option 2: Continue to deploy Chef Automate/Infra Server if required for existing infrastructure

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache SSL hardening that implements the same security controls
  
- **SSH Security**: The SSH compliance checks must be preserved
  - Approach: Convert the InSpec SSH profile to Ansible security role with equivalent checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
    - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Compliance Testing Framework**: The repository demonstrates using Chef InSpec for compliance testing with Ansible
  - Challenge: Finding an equivalent compliance testing framework in the Ansible ecosystem
  - Mitigation: Consider using Ansible Lint, Molecule, or maintaining InSpec as a standalone tool

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Challenge: Replacing this workflow with an Ansible-native testing approach
  - Mitigation: Implement Molecule for testing Ansible roles and playbooks

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Convert to proper Ansible role structure
   - Add documentation

2. **poodle-fix playbook** (low risk, already Ansible)
   - Convert to proper Ansible role structure
   - Add documentation

3. **InSpec compliance tests** (moderate complexity)
   - Convert to Ansible-native testing or maintain as InSpec tests
   - Update integration with Ansible

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks for equivalent functionality
   - Implement proper secret management

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
2. The InSpec tests are valuable and need to be preserved in some form
3. The Chef Automate/Infra Server deployment may still be needed for existing infrastructure
4. The target environment will continue to be Ubuntu 20.04 LTS
5. The security requirements (SSL hardening, SSH configuration) must be maintained
6. No external dependencies or integrations beyond what's visible in the repository
7. The deployment is for testing/demonstration purposes rather than production (based on self-signed certificates and simple configurations)
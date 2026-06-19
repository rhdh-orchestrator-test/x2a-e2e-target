# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web servers. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the deployment scripts into Ansible playbooks
3. Ensuring the compliance validation capabilities are preserved

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Integrate with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule can manage the test VM lifecycle similar to Test Kitchen

- **Chef Automate/Infra Server**: These deployment scripts can be replaced with:
  - Ansible playbooks for deploying alternative compliance platforms
  - Consider migrating to Ansible Tower/AWX for enterprise automation

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 is enforced in the Apache configuration
  - Maintain the same level of SSL/TLS security

- **SSH Hardening**: The SSH security controls tested by InSpec need to be implemented in Ansible
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with security standards referenced in the InSpec tests (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible's crypto modules with proper secret management

### Technical Challenges

- **Test Framework Migration**: Converting Chef InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Map InSpec resources to equivalent testinfra or pytest-ansible assertions

- **Compliance Validation**: Ensuring the same level of compliance validation
  - Challenge: Maintaining the security validation capabilities of InSpec
  - Mitigation: Document compliance controls and ensure equivalent coverage in the new testing framework

- **Deployment Script Conversion**: Converting bash-based Chef deployment scripts to Ansible
  - Challenge: Ensuring idempotent execution of installation steps
  - Mitigation: Use Ansible's package and service modules with proper state checking

### Migration Order

1. **website_https playbook** (already in Ansible, low risk)
   - Review and optimize the existing Ansible playbook
   - Add proper idempotence checks

2. **poodle_fix playbook** (already in Ansible, low risk)
   - Review and optimize the existing Ansible playbook
   - Ensure it works with the latest Apache versions

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible testing framework
   - Convert ssh_profile.rb to Ansible testing framework
   - Validate that tests provide equivalent coverage

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Consider alternative compliance platforms compatible with Ansible

5. **Test Kitchen Configuration** (moderate complexity)
   - Replace kitchen.yml with Molecule configuration
   - Ensure test VMs are properly provisioned and tested

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. The InSpec tests are used for validation only and not for remediation
3. The deployment scripts are used in development/testing environments and not production
4. The hardcoded credentials in the deployment scripts are for testing purposes only
5. The target environment will continue to be Ubuntu 20.04 or compatible
6. Vagrant will continue to be used for development/testing environments
7. The security compliance requirements (SRG-OS-000112, etc.) must be maintained
8. The Apache web server configuration requirements will remain the same
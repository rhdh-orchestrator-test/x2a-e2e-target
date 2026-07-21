# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in place) and moderate complexity for converting the InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1 files) in this repository. The repository primarily contains Ansible playbooks and Chef InSpec tests.

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Static HTML content for the website deployed by the Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules (ansible.builtin.assert, ansible.builtin.command with register)
  - Option 3: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific CI/CD pipeline using GitHub Actions or similar

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks to configure compliance scanning and reporting tools
  - Consider alternatives like AWX/Ansible Tower for centralized management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and SSLv3 remains disabled
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: The SSH security profile must be maintained
  - Convert the InSpec SSH profile to equivalent Ansible checks
  - Ensure root login remains disabled in SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities

- **Compliance Reporting**: Replacing Chef Automate's compliance reporting
  - Challenge: Chef Automate provides comprehensive compliance dashboards
  - Mitigation: Consider integrating with tools like Prometheus/Grafana or compliance-specific tools

- **Test Kitchen Workflow**: Replacing the existing testing workflow
  - Challenge: Current setup uses Test Kitchen for orchestrating tests
  - Mitigation: Implement Molecule for similar functionality with Ansible

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Verify and optimize existing website_https.yml and poodle_fix.yml playbooks
   - No conversion needed, just code review and potential optimization

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Molecule with Testinfra
   - Create equivalent tests for website_https_verify.rb and ssh_profile.rb

3. **Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Server deployment scripts
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. Compliance testing is a critical requirement that must be maintained
4. The deployment scripts for Chef Automate/Server will be replaced with equivalent Ansible automation
5. The target environment (Ubuntu 20.04) will remain the same
6. Test Kitchen workflow is important and needs an equivalent replacement
7. No additional Chef cookbooks or resources are being used beyond what's visible in the repository
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only
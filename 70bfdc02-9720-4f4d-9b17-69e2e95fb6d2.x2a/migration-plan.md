# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks and Chef InSpec tests. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as the Ansible playbooks can be largely reused and the InSpec tests need to be converted to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG/CCI)

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with testinfra or Goss
  - For compliance testing: Consider OpenSCAP with ansible-lockdown or Ansible Compliance as Code
  
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Automation Platform for automation and reporting
  - OpenSCAP for compliance scanning
  - AWX (open-source Ansible Tower) for workflow management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Replace self-signed certificates with Let's Encrypt integration where applicable

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Maintain compliance with security standards (STIG/CCI referenced in tests)

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to an Ansible-compatible testing framework while maintaining the same level of compliance validation
  - Mitigation: Use ansible-test, Molecule with testinfra, or integrate with OpenSCAP

- **Test Kitchen Integration**: Replacing Test Kitchen workflow with Ansible Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

- **Chef Automate Deployment**: If Chef Automate functionality is still needed, determining how to integrate with Ansible
  - Mitigation: Evaluate if Ansible Automation Platform can replace Chef Automate functionality or if a hybrid approach is needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can be directly used with minimal modifications
2. **Testing Framework**: Convert InSpec tests to Ansible-compatible testing (medium complexity)
3. **Deployment Scripts**: Convert Chef Automate/Server deployment scripts to Ansible roles (higher complexity)

### Assumptions

1. The primary goal is to migrate away from Chef InSpec while maintaining or improving the compliance testing capabilities
2. The existing Ansible playbooks are working correctly and follow best practices
3. There is no dependency on Chef-specific features that cannot be replicated in Ansible
4. The deployment scripts for Chef Automate/Server are intended to be replaced with equivalent Ansible automation
5. The security compliance requirements (STIG/CCI) mentioned in the InSpec tests must be maintained in the Ansible solution
6. Test Kitchen is used primarily for development and testing, not for production deployments
7. The self-signed certificates are for testing purposes and may need to be replaced with proper certificate management in production
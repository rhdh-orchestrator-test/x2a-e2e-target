# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for web server deployment with HTTPS configuration
2. Chef InSpec profiles for compliance testing
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on converting the InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-server-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for web server testing
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly defined in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex testing scenarios

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Create custom Ansible playbooks for test environment provisioning

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and control
  - Option 2: Use Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Preserve the existing Ansible task that enforces TLSv1.2 and disables older protocols

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Maintain the existing Ansible OpenSSL module usage or consider migrating to more modern certificate management

- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH security configuration
  - Approach: Create equivalent Ansible assertions or molecule tests to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password): 1 instance
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Ansible assert modules or Molecule verify phase with custom verifiers

- **Test Kitchen to Molecule**: Migrating the test infrastructure from Test Kitchen to Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the existing Test Kitchen configuration

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible equivalents
  - Mitigation: Create Ansible roles for configuration management platform deployment if needed, or document manual steps if Chef infrastructure is being fully replaced

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Action: Review and optimize existing Ansible playbooks
   - Effort: Low (1-2 days)

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Action: Convert to Ansible Molecule tests or equivalent
   - Effort: Medium (3-5 days)

3. **Test Kitchen Configuration** (kitchen.yml) - Medium complexity
   - Action: Replace with Molecule configuration
   - Effort: Medium (2-3 days)

4. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Action: Create Ansible playbooks for equivalent functionality if needed
   - Effort: High (5-7 days)

### Assumptions

1. The primary goal is to migrate all testing and deployment to Ansible-native solutions
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
3. Chef InSpec tests need to be replaced with equivalent Ansible testing mechanisms
4. The Chef server deployment scripts may be obsolete if moving entirely to Ansible
5. No external dependencies or modules beyond what's visible in the repository
6. The target environment will remain Ubuntu 20.04 or compatible Linux distribution
7. The migration will maintain the same security posture and compliance checks
8. No custom Chef resources or complex Chef-specific functionality is present
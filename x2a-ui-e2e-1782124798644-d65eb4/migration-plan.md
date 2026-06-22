# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully migrate all components to pure Ansible. The primary focus will be on replacing Chef InSpec tests with Ansible-native solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use [ansible-lint](https://ansible-lint.readthedocs.io/) for static analysis
  - Option 2: Use [Molecule](https://molecule.readthedocs.io/) for Ansible role testing
  - Option 3: Use [OpenSCAP](https://www.open-scap.org/) with Ansible for compliance testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for configuration management
  - Consider migrating to Ansible Tower/AWX for enterprise management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **SSH Hardening**: Maintain the SSH security controls from ssh_profile.rb
  - Convert InSpec controls to Ansible tasks that enforce the same security policies
  - Consider using ansible-lockdown or similar security role

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially with ansible-vault or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use ansible.builtin.assert or community.general.assert modules to create equivalent tests
  - Consider OpenSCAP integration for compliance testing

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow with Ansible-native testing
  - Mitigation: Implement Molecule for similar functionality with Ansible focus

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Consider Ansible Tower/AWX with compliance scanning plugins or integration with security tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and update as needed for current Ansible best practices
   - Consolidate into roles if appropriate

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible assertion tasks or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Consider if this functionality is still needed or if it should be replaced with Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The hardcoded credentials in the deployment scripts are examples and not used in production
3. The Test Kitchen configuration is primarily for testing and demonstration
4. There are no external dependencies or integrations not visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible
6. The migration will maintain the same level of security compliance checking
7. No custom Chef resources or complex Chef-specific functionality is in use
# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as the repository already contains Ansible playbooks. The migration will primarily involve:

1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Consolidating the deployment scripts for Chef Automate and Chef Server into Ansible playbooks
3. Ensuring all compliance checks are maintained during the migration

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment. Can be reused as-is in the Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic compliance checks
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Integrate with other compliance tools like OpenSCAP or Ansible Compliance

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper documentation
  
- **SSH Security Controls**: The SSH root login check must be maintained
  - Approach: Convert the InSpec control to an Ansible task that checks and enforces the SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios
  
- **Maintaining Compliance Standards**: Ensuring that all compliance checks (especially the STIG-referenced SSH control) are properly maintained
  - Mitigation: Document all compliance requirements and ensure they are covered in the new Ansible roles

### Migration Order

1. **website_https playbook** (already in Ansible, low risk)
   - Convert to a proper Ansible role structure
   - Add documentation

2. **poodle_fix playbook** (already in Ansible, low risk)
   - Convert to a proper Ansible role structure
   - Add documentation

3. **Chef Automate and Chef Server deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible roles
   - Implement Ansible Vault for credential storage

4. **InSpec tests** (highest complexity)
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are maintained

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The Chef InSpec tests are used for compliance verification only and not for configuration management.

3. The deployment scripts for Chef Automate and Chef Server are used for demonstration purposes and contain simplified configurations.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. There are no external dependencies or integrations beyond what is explicitly shown in the repository.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in a production environment.

7. The migration will focus on maintaining the same functionality and compliance checks while moving to a pure Ansible solution.
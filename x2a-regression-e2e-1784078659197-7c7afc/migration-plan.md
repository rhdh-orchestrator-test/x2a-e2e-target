# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring a secure web server with HTTPS
2. Chef InSpec tests for verifying compliance and security requirements

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on replacing Chef InSpec tests with equivalent Ansible testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled according to security requirements
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Integration with other compliance tools like OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for setting up alternative compliance and automation platforms:
  - Option 1: AWX/Ansible Tower for automation
  - Option 2: Compliance solution like OpenSCAP or Compliance as Code

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **SSH Security Controls**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This compliance check must be preserved in the Ansible solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate and key management
  - Consider migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec tests with equivalent Ansible-native testing solutions while maintaining the same level of compliance validation.
  - Mitigation: Evaluate Molecule with testinfra or OpenSCAP integration for Ansible.

- **Test Execution Framework**: Test Kitchen is used to orchestrate the testing workflow. A replacement framework for Ansible will be needed.
  - Mitigation: Implement Molecule as the test orchestration framework.

- **Chef Automate Replacement**: The Chef Automate deployment scripts need to be replaced with equivalent Ansible automation.
  - Mitigation: Create Ansible playbooks to deploy AWX/Tower or other compliance platforms.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as these are already in Ansible format and can be preserved with minimal changes.
2. **Testing Framework**: Replace Test Kitchen with Molecule for test orchestration.
3. **Compliance Tests**: Migrate Chef InSpec tests to Ansible-compatible testing solutions.
4. **Deployment Scripts**: Replace Chef Automate/Infra Server deployment scripts with Ansible playbooks.

### Assumptions

1. The primary goal is to eliminate Chef dependencies while preserving the existing Ansible playbooks.
2. The compliance testing functionality provided by Chef InSpec is still required in the migrated solution.
3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
4. The security requirements specified in the InSpec tests (especially SSH hardening) must be maintained.
5. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.
7. The self-signed certificates are acceptable for the demonstration environment, but production deployments would require proper certificate management.
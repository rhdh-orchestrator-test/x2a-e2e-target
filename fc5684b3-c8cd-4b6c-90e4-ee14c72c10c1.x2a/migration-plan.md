# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example project demonstrating Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server installation, Chef Automate installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2.
- `chef-and-ansible/index.html`: Sample HTML file used for testing the web server deployment.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control that verifies SSH root login is disabled for security compliance.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts could be used in any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing of Ansible results

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles for:
  - Configuration management server setup
  - Compliance automation server setup

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLS 1.2 remains enabled and older protocols remain disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Preserve the security checks from ssh_profile.rb
  - Convert InSpec controls to Ansible assertions or Molecule verifiers
  - Maintain compliance with security benchmarks (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use Ansible Molecule with custom verifiers or pytest-ansible for similar functionality

- **Compliance Reporting**: InSpec provides built-in compliance reporting
  - Challenge: Replicating compliance reporting capabilities in Ansible
  - Mitigation: Integrate with tools like Ansible AWX/Tower for reporting or use community modules for compliance reporting

### Migration Order

1. **chef-and-ansible**: Low risk as the Ansible playbooks can remain largely unchanged, focus on converting InSpec tests
2. **setup-automate**: Convert Chef server and Automate deployment scripts to Ansible roles

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't require significant modifications
3. There's no requirement to maintain backward compatibility with Chef InSpec
4. The deployment scripts are used for setting up development/test environments and not production systems (given the hardcoded credentials)
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. Vagrant will continue to be used for development/testing environments
7. No external Chef cookbooks or complex Chef-specific features are in use that would require special handling
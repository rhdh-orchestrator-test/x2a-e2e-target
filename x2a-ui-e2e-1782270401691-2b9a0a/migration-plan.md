# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

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
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate to Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing where more complex validation is needed

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and UI
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable older protocols
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH compliance checks must be preserved
  - Convert InSpec SSH controls to Ansible assertions or Molecule verifiers
  - Maintain STIG compliance references for documentation

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Replace with Ansible Vault for secure credential storage
  - Consider integrating with external secret management systems like HashiCorp Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting Ruby-based InSpec tests to Ansible-native testing
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use combination of Ansible assert module, Molecule verifiers, and potentially custom Python test modules

- **Chef Automate Functionality**: Replacing Chef Automate's compliance dashboard
  - Challenge: Chef Automate provides integrated compliance reporting
  - Mitigation: Consider solutions like Prometheus/Grafana for metrics and compliance dashboards, or ELK stack for log analysis

- **STIG Compliance**: Maintaining security compliance documentation
  - Challenge: InSpec tests include detailed STIG references and documentation
  - Mitigation: Ensure all compliance metadata is preserved in Ansible documentation or separate compliance documentation

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as these are already in Ansible format
   - Update to current Ansible best practices and module syntax

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Convert to Ansible roles for infrastructure deployment
   - Replace with AWX/Tower installation if that's the chosen replacement

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functional and follow best practices
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment scripts are used for setting up test/development environments and not production systems (given the hardcoded credentials)
5. There is no requirement to maintain backward compatibility with Chef InSpec
6. The STIG compliance requirements must be maintained in the new solution
7. The self-signed certificates in the website_https.yml playbook are acceptable for the use case (not requiring trusted CA certificates)
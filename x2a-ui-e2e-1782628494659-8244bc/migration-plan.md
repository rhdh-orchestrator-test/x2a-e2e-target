# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

**Complexity**: Low to Medium - The InSpec tests are straightforward, but ensuring equivalent test coverage in Ansible will require careful implementation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are preserved in the Apache configuration
  - Maintain the same level of TLS security (TLSv1.2 only)

- **SSH Hardening**: The SSH root login check must be preserved
  - Convert the InSpec control to an equivalent Ansible check
  - Maintain the STIG compliance references for documentation

- **Certificate Management**: Self-signed certificate generation must be preserved
  - The openssl_* modules are already Ansible-native and can be kept as-is

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Test Coverage**: Ensuring that Ansible-native testing provides the same level of validation as InSpec
  - Mitigation: Create a test coverage matrix to ensure all InSpec tests have equivalent Ansible assertions
  - Consider using Molecule scenarios to replicate the InSpec test cases

- **Compliance Validation**: InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting in Ansible or integrate with a compliance tool like OpenSCAP

- **Chef Automate Functionality**: Replacing Chef Automate's compliance dashboard
  - Mitigation: Evaluate Ansible AWX/Tower compliance capabilities or integrate with a third-party compliance dashboard

### Migration Order

1. **website_https_verify.rb** (Priority 1, low risk)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Validate against existing Ansible playbook

2. **ssh_profile.rb** (Priority 2, low risk)
   - Convert InSpec control to Ansible assertions
   - Maintain compliance metadata

3. **deploy-automate.sh and deploy-chef-server.sh** (Priority 3, moderate complexity)
   - Convert to Ansible playbooks
   - Implement Ansible Vault for credentials
   - Test deployment in isolated environment

4. **kitchen.yml** (Priority 4, low risk)
   - Replace with Molecule configuration or update for Ansible-only testing

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) will remain largely unchanged
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The deployment will continue to use self-signed certificates rather than Let's Encrypt or other CA
4. The SSH hardening requirements will remain aligned with the specified STIG controls
5. The Chef Automate and Chef Server deployment scripts are used for setting up test environments and not production systems
6. No external data sources or databases are required for the applications
7. The migration does not need to address scaling or high-availability concerns
8. The current implementation does not use encrypted secrets or external credential stores
# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
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
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider ansible-test for unit testing
  - For compliance testing similar to InSpec, evaluate:
    - OpenSCAP with ansible-playbook
    - Ansible Compliance as Code framework
    - Ansible Automation Platform's built-in compliance capabilities

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to an equivalent Ansible assertion or Molecule verification

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 3 credential sets identified (username, password, email)

- **Certificate Management**: 
  - Self-signed certificates are generated in the website_https.yml playbook
  - Consider using Ansible's crypto modules more extensively for certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing style to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module and custom modules where needed
  - Consider developing custom Ansible modules for complex compliance checks

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs equivalent functionality
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with a third-party compliance tool

- **Chef Automate Functionality**: The Chef Automate deployment provides features that need Ansible equivalents
  - Mitigation: Map Chef Automate features to Ansible Automation Platform capabilities
  - Consider AWX/Tower for web UI and API functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain in Ansible format
   - Review and update to current Ansible best practices
   - Implement Ansible Vault for any sensitive data

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible Molecule tests
   - Ensure equivalent compliance checks are maintained

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Convert to Ansible roles for Chef Automate and Chef Server deployment
   - Alternatively, create Ansible playbooks for deploying Ansible Automation Platform instead

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functional and follow best practices
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment scripts are used for setting up test environments and not production systems
5. No external Chef cookbooks or complex Chef-specific features are in use
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. The Test Kitchen configuration is primarily used for testing and not for production deployments
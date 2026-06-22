# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_website_test**:
    - Description: Chef InSpec test that verifies HTTPS functionality and website content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol verification

- **inspec_ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef_automate_deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for enterprise automation
  - Or GitLab CI/CD pipelines for a more lightweight approach

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Approach: Ensure the Ansible playbook continues to enforce the same SSL protocol restrictions

- **SSH Security**: The SSH root login restriction must be maintained
  - Approach: Convert the InSpec test to an Ansible task that ensures the same SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the InSpec tests to Ansible-native testing solutions will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Verification**: Ensuring that all compliance checks are properly translated
  - Mitigation: Create a compliance matrix to track each control and its implementation in Ansible

- **Chef Server Deployment**: Replacing the Chef server deployment with an equivalent Ansible Tower/AWX setup
  - Mitigation: Document the Chef server functionality being used and map to Ansible Tower/AWX features

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize existing Ansible playbooks
   - Consolidate into a single playbook with roles if appropriate

2. **inspec_website_test** and **inspec_ssh_profile** (moderate complexity)
   - Convert InSpec tests to Ansible-native testing
   - Validate that all compliance checks are maintained

3. **chef_automate_deploy** and **chef_server_deploy** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Infra Server deployment
   - Or document migration to AWX/Ansible Tower

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are being used for compliance verification of Ansible-managed systems
3. There may be additional Chef cookbooks or InSpec profiles not included in this repository
4. The deployment scripts are templates that would be customized for actual deployments
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The Test Kitchen configuration is used for testing and development, not for production deployments
7. The target environment is Ubuntu 20.04 running on Vagrant VMs
8. The Apache web server configuration is a simplified example and may need additional security hardening
9. The self-signed certificates are for testing purposes and would be replaced with proper certificates in production
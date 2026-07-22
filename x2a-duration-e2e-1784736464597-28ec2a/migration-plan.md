# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need to be consolidated into a pure Ansible solution. The repository appears to be a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation. The main components are:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying the Ansible configurations and SSH security
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 days of work, with low complexity since most of the content is already in Ansible format.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

**Note: I have thoroughly searched the repository using file_search for the following patterns:**
- `**/manifests/init.pp` - No Puppet modules found
- `**/recipes/default.rb` - No Chef cookbooks found
- `**/*.psd1` - No PowerShell modules found

Therefore, there are no traditional Puppet modules, Chef cookbooks, or PowerShell modules in this repository that would require separate entries in the MODULE INVENTORY.

The repository contains the following components:

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, creates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL security hardening, Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website configuration, checking port 443, HTTP status, content, and SSL protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL protocol security testing

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance testing with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier
- `README.md`: Documentation explaining the purpose of the repository as examples for Chef InSpec with Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use the ansible.builtin.assert module for inline testing
  - Option 3: Keep InSpec but integrate it with Ansible using the community.general.inspec module

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the kitchen-ansible plugin (already in use)

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configuration that must be preserved:
  - Self-signed certificate generation
  - Disabling vulnerable SSL protocols (SSLv3)
  - Enabling secure TLS protocols (TLSv1.2)

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Root login disabled
  - Compliance with security standards (STIG)

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab
  - These should be moved to Ansible Vault or another secure secret management solution

- **Vault/secrets management**:
  - No existing vault implementation detected
  - 2 credential sets identified in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the InSpec resource models (port, http, ssl, sshd_config)
  - Creating equivalent Ansible assertions or Molecule tests
  - Ensuring the same level of compliance verification
  - Preserving STIG compliance references and documentation

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible roles:
  - System requirements configuration (sysctl settings)
  - Package installation and configuration
  - User and organization management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Consolidate handlers and variables
   - Add documentation

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible Molecule tests or inline assertions
   - Ensure all compliance checks are preserved
   - Maintain STIG references and security documentation

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles for infrastructure deployment
   - Implement secure credential management
   - Test thoroughly to ensure equivalent functionality

### Assumptions

1. The repository is primarily for demonstration purposes and not a production deployment
2. The InSpec tests are essential for compliance verification and must be preserved in some form
3. The hardcoded credentials in the deployment scripts are examples and not actual production credentials
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The Apache configuration and SSL settings are representative of actual security requirements
6. The migration will consolidate to pure Ansible without maintaining Chef components
7. Test Kitchen may still be used as a testing framework with the Ansible provisioner
8. STIG compliance requirements in the InSpec tests must be maintained in the Ansible implementation
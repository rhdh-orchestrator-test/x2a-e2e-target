# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2 protocol

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts could be used in any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's `assert` module for basic testing within playbooks
  - **Option 2**: Implement Molecule for Ansible role testing
  - **Option 3**: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks
  - Molecule supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management solutions
  - For compliance reporting, consider integrating with tools like OpenSCAP or Ansible's built-in compliance capabilities

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH compliance checks in ssh_profile.rb must be maintained
  - Convert the InSpec control to equivalent Ansible assertions or Molecule tests
  - Maintain the STIG compliance references for documentation

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert, wait_for, and uri modules to replicate InSpec functionality

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The scripts install Chef-specific components that may not be needed in an Ansible-only environment
  - Mitigation: Determine if Chef Automate/Server functionality is still required or if it can be replaced with Ansible AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update as needed for current best practices
   - Add documentation and comments

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are maintained

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Determine if Chef Automate/Server is still needed
   - If not, create equivalent Ansible playbooks for setting up Ansible AWX/Tower
   - If yes, create Ansible playbooks that install and configure Chef components

### Assumptions

1. The primary purpose of this repository is to demonstrate InSpec with Ansible, not for production use
2. The hardcoded credentials in deployment scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There is no requirement to maintain Chef Automate/Server functionality if moving to an Ansible-only solution
5. The security compliance requirements (STIG references) need to be maintained in the new testing framework
6. The repository does not contain any custom Chef cookbooks that would need migration
7. The deployment scripts are intended for demonstration/lab environments, not production deployments
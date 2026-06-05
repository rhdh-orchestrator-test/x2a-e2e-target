# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a template for the website. Can be preserved as-is or converted to an Ansible template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure validation: Use Ansible assert module or custom modules
  - For compliance testing: Consider integrating with tools like OpenSCAP or using Ansible's built-in assert module
  - Alternative: Use Ansible Lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Can use the same Vagrant driver for local testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the only enabled protocol
  - Consider updating to also include TLSv1.3 for modern security standards

- **SSH Security**: The SSH root login check must be preserved
  - Convert the InSpec control to an Ansible task that checks and enforces this setting
  - Consider expanding to include additional SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, possibly using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions will require careful mapping of test logic
  - Challenge: InSpec has specialized resources for testing SSL/TLS configurations
  - Mitigation: May need to create custom Ansible modules or use shell commands with assert

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The scripts install Chef-specific components that may not have direct Ansible equivalents
  - Mitigation: Create Ansible roles that perform equivalent setup for compliance and configuration management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or Molecule tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for infrastructure setup

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation, not to provide production-ready infrastructure
2. The InSpec tests are intended to validate the Ansible playbooks, not to be run independently
3. The deployment scripts are examples and may contain simplified configurations not suitable for production
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's explicitly shown in the code
6. The migration will focus on preserving functionality rather than enhancing it
7. No CI/CD pipeline integration is currently in place
8. The hardcoded credentials in deployment scripts are for demonstration purposes only
9. The self-signed certificates are acceptable for the demonstration environment
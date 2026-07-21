# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on infrastructure automation and compliance testing. The primary content consists of Ansible playbooks with Chef InSpec tests for compliance verification, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) in this repository. The repository primarily contains Ansible playbooks and Chef InSpec tests, along with Chef deployment scripts.

The following components need to be migrated:

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a template. Migration consideration: Can be directly used in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module for HTTP checks and community.crypto modules for SSL verification
  - For ssh_profile.rb: Use ansible-lint or OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain the security hardening that disables SSLv3 and enables only TLSv1.2.
  - Migration approach: Use Ansible's apache2_module and lineinfile/template modules to apply the same security configurations.

- **SSH Security**: The InSpec profile checks for SSH root login configuration.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks.
  - Mitigation: Use Ansible's assert module combined with command/shell modules to perform similar checks, or integrate with ansible-test.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles.
  - Mitigation: Create Ansible roles that perform equivalent system configuration and software installation steps.

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format, just need organization into roles
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity, requires conversion to Ansible testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity, requires creating equivalent Ansible roles

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "examples" and "companion to a white paper".
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed with Ansible, showing an integration pattern between Chef and Ansible tools.
3. The setup-automate scripts are independent from the chef-and-ansible directory and represent a separate use case for Chef infrastructure deployment.
4. The migration goal is to convert all components to pure Ansible, including replacing InSpec tests with Ansible-native testing solutions.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in the migrated solution.
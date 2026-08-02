# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server setup. The migration scope is relatively small, focusing on:

1. Ansible playbooks for web server configuration with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer to complete the migration. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure automation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Shell script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Static HTML content for the web server. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX
  - Migration will involve setting up equivalent users, organizations, and permissions

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure that:
  - Self-signed certificates are replaced with proper CA-signed certificates in production
  - Modern TLS protocols are enforced (already addressed in poodle_fix.yml)
  - Cipher suites are properly configured

- **SSH Hardening**: The InSpec profile checks for SSH root login. Ensure that:
  - SSH hardening is implemented in Ansible playbooks
  - Compliance checks are maintained in the new testing framework

- **Credentials Management**: 
  - The setup scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Detected credentials:
    - automate-deploy: 1 password in plaintext
    - chef-server-deploy: 1 password in plaintext

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for each InSpec resource and its Ansible equivalent.

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance reporting in the Ansible ecosystem.
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party compliance tools.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. Only need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing or Molecule scenarios.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README indicating it's for "examples" and "content created by Technical Product Marketing."
2. The InSpec tests are intended to verify compliance of systems managed by Ansible, not necessarily systems managed by Chef.
3. The deployment scripts are used for setting up Chef infrastructure, which would be replaced by Ansible infrastructure in the migrated solution.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The migration goal is to standardize on Ansible and eliminate Chef dependencies where possible.
6. The self-signed certificates in the playbooks are for testing purposes and would be replaced with proper certificates in production.
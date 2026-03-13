# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, primarily involving:

1. Chef InSpec tests that are used alongside Ansible playbooks
2. Chef Automate and Chef Infra Server deployment scripts
3. Ansible playbooks for web server configuration and security hardening

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be converting InSpec tests to Ansible-compatible testing frameworks and replacing Chef server deployment scripts with Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache2
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache2 configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for hardening SSL configuration to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Use community.general.assert module for basic tests
  - Option 3: Implement ansible-lint for static analysis

- **Test Kitchen (latest)**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for Ansible content management
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The current implementation hardens Apache against POODLE vulnerability. Ensure Ansible playbooks maintain or improve this security posture.
  - Migration approach: Preserve the SSL hardening in the Ansible playbooks, potentially enhancing with more current best practices.

- **SSH Hardening**: Current InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule with testinfra.

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Maintain this capability but consider adding support for Let's Encrypt as an alternative.

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials.
  - Migration approach: Use Ansible Vault for secure credential storage.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Molecule with testinfra which provides similar functionality to InSpec.

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents.
  - Mitigation: AWX/Ansible Tower can provide similar functionality for job scheduling and reporting.

- **Compliance Reporting**: Chef Automate provides compliance reporting capabilities.
  - Mitigation: Consider integrating with tools like OpenSCAP or Compliance as Code solutions.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, convert to Ansible-compatible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, replace with Ansible playbooks for infrastructure setup.

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
3. The migration will maintain the same level of security compliance checking.
4. Users will have basic familiarity with Ansible concepts.
5. The hardcoded credentials in deployment scripts are for demonstration purposes only.
6. The repository is not using any Chef cookbooks that would require complex migration.
7. The InSpec tests are primarily used for verification rather than remediation.
8. The deployment scripts are used for setting up test environments rather than production systems.
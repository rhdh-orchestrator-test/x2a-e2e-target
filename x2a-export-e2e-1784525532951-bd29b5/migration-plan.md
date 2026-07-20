# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL and InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Should be migrated to Ansible test framework or maintained as InSpec test.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible test framework or maintained as InSpec test.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Ansible Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - Alternatively, maintain InSpec tests but integrate them into Ansible workflow

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Vagrant can still be used as a driver for Molecule

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for configuration management
  - Consider if Chef Automate functionality needs to be replaced with alternatives like AWX/Ansible Tower

### Security Considerations

- **SSL Configuration**: The migration must maintain the secure SSL configuration (TLSv1.2) and disable vulnerable protocols (SSLv3)
  - Approach: Preserve the same Apache SSL configuration in the Ansible playbooks

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Approach: Ensure Ansible playbooks include SSH hardening tasks that meet the same compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated during deployment but should be managed securely
  - Count of credentials detected:
    - setup-automate: 3 credentials (username, password, organization name)

### Technical Challenges

- **InSpec Test Integration**: Determining whether to maintain InSpec tests or migrate to Ansible-native testing
  - Mitigation: Short-term, keep InSpec tests and integrate them into Ansible workflow; long-term, consider migrating to Ansible-native testing

- **Chef Automate Functionality**: Determining if any Chef Automate functionality needs to be replaced
  - Mitigation: Assess if AWX/Ansible Tower or other tools are needed to replace Chef Automate functionality

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format, just need integration into new structure
2. **Chef Deployment Scripts** (setup-automate/*.sh): Medium complexity, requires converting Bash scripts to Ansible playbooks
3. **Testing Framework** (InSpec tests): Medium complexity, requires decision on testing approach

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README.md description.
2. The Chef Automate and Chef Infra Server deployment is a standalone component that can be replaced with equivalent Ansible functionality.
3. The InSpec tests are valuable for compliance verification and should either be maintained or have equivalent functionality in the Ansible solution.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in production.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be flexible enough for cloud deployments.
6. There are no external dependencies or integrations beyond what's visible in the repository.
7. The Apache HTTPS configuration is a standalone example and not part of a larger web application infrastructure.
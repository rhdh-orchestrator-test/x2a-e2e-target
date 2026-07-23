# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and shell scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified all paths using `list_directory` and confirmed that no Puppet modules (`**/manifests/init.pp`), Chef cookbooks (`**/recipes/default.rb`), or PowerShell modules (`**/*.psd1`) exist in this repository. The repository primarily contains Ansible playbooks and Chef InSpec tests.

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test that verifies HTTPS configuration. Will need to be converted to Ansible tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Will need to be converted to Ansible security tests.
- `chef-and-ansible/index.html`: Sample HTML file used by the website_https playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **InSpec Tests**: Convert to Ansible-native testing using:
  - ansible-test for unit testing
  - testinfra for infrastructure testing
  - ansible-lint for playbook linting
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for infrastructure management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain or improve security posture:
  - Ensure proper TLS protocol versions (TLSv1.2+)
  - Maintain self-signed certificate generation or integrate with Let's Encrypt
  - Preserve file permissions (mode: 0640) for sensitive files

- **SSH Hardening**: The SSH compliance profile checks for root login restrictions. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Maintain compliance with security benchmarks (referenced SRG-OS-000112)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks will require careful mapping of test assertions.
  - Mitigation: Use testinfra which has similar syntax to InSpec for infrastructure testing.

- **Chef Automate Deployment**: The Chef Automate deployment scripts contain specific configurations that need to be preserved.
  - Mitigation: Create dedicated Ansible roles for Chef Automate deployment or consider migrating to alternative solutions like AWX/Tower.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Restructure into proper Ansible role format
2. **poodle_fix.yml** (low risk, already Ansible): Restructure into proper Ansible role format
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing
4. **Chef Deployment Scripts** (high complexity): Convert to Ansible roles or consider alternative solutions

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. The migration aims to maintain the same functionality while improving structure and maintainability.
3. There are no external dependencies or integrations not visible in the repository.
4. The Chef Automate and Chef Infra Server deployment scripts may be replaced with alternative configuration management solutions rather than direct Ansible equivalents.
5. The security requirements specified in the InSpec tests (particularly SSH hardening) must be maintained in the migrated solution.
6. Test Kitchen is currently used for development and testing, and an equivalent workflow will be needed in the Ansible migration.
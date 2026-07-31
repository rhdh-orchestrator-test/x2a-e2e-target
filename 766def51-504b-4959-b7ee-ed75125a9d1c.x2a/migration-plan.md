# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities of Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec profile to verify SSH security configuration (root login disabled)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Replace with Ansible's built-in assert module for basic tests
  2. Use community.general.test_module for more complex assertions
  3. Keep InSpec for compliance testing and integrate with Ansible using the inspec_exec module
  4. Migrate to Ansible Lint for static analysis

- **Test Kitchen**: Currently used for testing Ansible playbooks.
  - Replace with Molecule for Ansible role/collection testing

- **Chef Automate/Infra Server**: Currently deployed via bash scripts.
  - Create Ansible playbooks to deploy Chef Automate/Infra Server or migrate to Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should:
  - Maintain or improve the TLS security settings (currently TLSv1.2 only)
  - Use Ansible Vault for storing certificate information
  - Consider using Let's Encrypt for certificate management instead of self-signed certificates

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled.
  - Implement equivalent checks using Ansible's assert module
  - Consider using ansible.posix.sshd_config module for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or molecule tests will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Automate/Server Deployment**: The current deployment uses bash scripts with specific Chef commands.
  - Mitigation: Research Ansible modules for Chef management or create custom modules if needed

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, just needs restructuring into a proper role
2. **poodle_fix.yml** (Priority 1): Simple playbook, easy to convert to a role or include in the website_https role
3. **InSpec Tests** (Priority 2): Convert to Ansible assertions or Molecule tests
4. **Chef Deployment Scripts** (Priority 3): Create Ansible playbooks for Chef Automate/Server deployment

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the compliance testing capabilities
2. Chef InSpec may still be used for compliance testing even after migration to Ansible
3. The current Ansible playbooks are functional but need restructuring into proper roles and collections
4. The target environment will remain Ubuntu 20.04 or compatible
5. The deployment scripts for Chef Automate/Server are used for infrastructure setup, not application deployment
6. No external dependencies or third-party modules are used in the current Ansible playbooks
7. The hardcoded credentials in the deployment scripts are for testing purposes only
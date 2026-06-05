# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a template for the website deployment. Can be preserved as-is or converted to an Ansible template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios
  - Option 4: Convert InSpec tests to Ansible playbooks with assert statements

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or use Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration preserves the security hardening (TLSv1.2 only).
  - Migration approach: Preserve the existing Ansible tasks that configure SSL/TLS.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this compliance check is preserved.
  - Migration approach: Convert the InSpec test to an Ansible assert task or Molecule test.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider using Let's Encrypt for production.
  - Migration approach: Enhance the existing Ansible tasks to optionally use Let's Encrypt.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible assertions or another testing framework.
  - Mitigation: Use Ansible's `assert` module with appropriate conditions or consider using Molecule which has good integration with Ansible.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features.
  - Mitigation: Implement Ansible AWX/Tower with custom reporting or integrate with compliance tools like OpenSCAP.

- **Test Kitchen Integration**: Replacing Test Kitchen's integration with both Ansible and InSpec.
  - Mitigation: Use Molecule which is designed specifically for testing Ansible roles.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule or other Ansible testing framework

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes.
2. The primary goal is to eliminate Chef dependencies while preserving functionality.
3. The InSpec tests need to be converted to an Ansible-compatible testing framework.
4. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality.
5. The repository is primarily used for demonstration/educational purposes rather than production deployment.
6. No external dependencies or integrations beyond what's visible in the repository.
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
8. The security compliance requirements (STIG references in ssh_profile.rb) need to be preserved in the migrated solution.
# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2, restarts Apache and SSH services

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server setup. Can be preserved as-is or incorporated into Ansible as a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD with Ansible for automation pipelines

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration preserves the security settings that disable vulnerable protocols (SSLv3) and enable secure ones (TLSv1.2).
  - Migration approach: Preserve the existing Ansible tasks that configure SSL in Apache.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Convert the InSpec test to an Ansible assert or Molecule test.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider enhancing security by integrating with Let's Encrypt for production environments.
  - Migration approach: Add optional Let's Encrypt integration to the Ansible playbook.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded passwords.
  - Migration approach: Use Ansible Vault to securely store credentials.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches.
  - Mitigation: Start with simple assertions and gradually build more complex tests.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced in the Ansible ecosystem.
  - Mitigation: Clearly map Chef Automate features to Ansible equivalents before beginning migration.

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing with Ansible and InSpec.
  - Mitigation: Evaluate Molecule as a replacement that's more native to the Ansible ecosystem.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for infrastructure setup.
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Ansible-native testing framework.

### Assumptions

1. The primary goal is to eliminate Chef dependencies while preserving Ansible components.
2. The existing Ansible playbooks are working correctly and don't need functional changes.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The security compliance requirements (STIG references in ssh_profile.rb) need to be maintained.
5. The repository is primarily for demonstration/educational purposes rather than production use, given the nature of the examples and documentation references.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.
7. The self-signed certificates are acceptable for the demonstration environment but might need to be replaced with proper certificates in production.
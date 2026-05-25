# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef server and Automate deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with InSpec tests and Chef server deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework configuration.
- `index.html`: Static HTML content used in the website deployment. Can be reused as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Molecule for integration testing
  - **Option 2**: Ansible Test Framework for unit testing
  - **Option 3**: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with:
  - **Option 1**: Ansible Molecule for test orchestration
  - **Option 2**: Custom Ansible playbook with assert tasks for verification

- **Chef Server/Automate**: Replace with:
  - **Option 1**: Ansible AWX/Tower for enterprise automation platform
  - **Option 2**: GitLab CI/CD or Jenkins for pipeline orchestration

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml that enforces TLSv1.2 and disables vulnerable protocols.
  - Migration approach: Preserve the same configuration parameters in Ansible tasks.

- **SSH Security**: The SSH root login check in ssh_profile.rb must be maintained.
  - Migration approach: Convert to Ansible assert tasks that verify the same SSH configuration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - Self-signed certificates generated in the playbook should use the same secure parameters.
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar validation.

- **Chef Server/Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Server and Automate functionality.
  - Mitigation: Evaluate AWX/Tower or other CI/CD tools based on specific requirements.

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already Ansible playbooks, no migration needed.
2. **InSpec Tests**: Convert to Ansible assert tasks or Molecule tests.
   - website_https_verify.rb
   - ssh_profile.rb
3. **Chef Server/Automate Deployment Scripts**: Convert to Ansible playbooks.
   - deploy-chef-server.sh
   - deploy-automate.sh

### Assumptions

1. The primary purpose of this repository is to demonstrate InSpec with Ansible rather than being a production deployment.
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration will maintain the same level of security compliance checking currently provided by InSpec.
7. Test Kitchen is only used for development/testing and not for production deployments.
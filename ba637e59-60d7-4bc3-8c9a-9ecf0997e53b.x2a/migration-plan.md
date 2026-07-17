# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that are used together to deploy and verify secure web server configurations. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible's native testing capabilities while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The existing Ansible playbooks can be maintained with minimal changes, while the InSpec tests need to be converted to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for verifying HTTPS configuration.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec tests for verifying SSH security configuration.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests.
- `chef-and-ansible/index.html`: Sample HTML content for the web server.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality to Test Kitchen but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Consider using AWX or Ansible Tower as alternatives to Chef Automate for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the Ansible migration maintains:
  - Proper certificate generation
  - Secure protocol settings (TLSv1.2)
  - Disabled vulnerable protocols (SSLv3)

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests will require understanding the equivalent testing patterns in Ansible.
  - Mitigation: Create a mapping of InSpec resource types to Ansible modules and assertions.

- **Deployment Script Conversion**: The Chef Automate and Chef Infra Server deployment scripts need to be converted to idempotent Ansible playbooks.
  - Mitigation: Break down the scripts into discrete tasks and use Ansible's package management and command modules.

- **Integration Testing**: Ensuring the new Ansible testing framework provides the same level of compliance verification as InSpec.
  - Mitigation: Create a test matrix to verify all original InSpec tests have equivalent Ansible tests.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk as they can be maintained with minimal changes
2. **InSpec Tests** (chef-and-ansible/tests/website_https_verify.rb, chef-and-ansible/tests/ssh_profile.rb): Convert to Ansible testing framework
3. **Deployment Scripts** (setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh): Convert to Ansible playbooks
4. **Test Infrastructure** (chef-and-ansible/kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes.
2. The InSpec tests are currently being used for compliance verification and need to be maintained in some form.
3. The deployment scripts for Chef Automate and Chef Infra Server are still relevant and need to be converted to Ansible.
4. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
5. The security requirements specified in the InSpec tests (especially SSH configuration) must be maintained.
6. No external Chef cookbooks or dependencies are being used beyond what's in the repository.
7. The migration will not involve changes to the application functionality, only to the deployment and testing infrastructure.
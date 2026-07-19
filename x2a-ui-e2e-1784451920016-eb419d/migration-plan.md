# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on migrating the Chef InSpec tests to Ansible while maintaining or enhancing the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

The migration complexity is relatively low as most of the repository already consists of Ansible playbooks. The main effort will be in converting the Chef InSpec tests to Ansible equivalents and migrating the Chef server deployment scripts to Ansible playbooks. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **inspec_tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality, security, and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification, SSH security compliance

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server. Can be reused as-is in the Ansible playbook.
- `chef-and-ansible/website_https.yml`: Ansible playbook for setting up HTTPS website.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration.
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices enforcement

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Use existing Vagrant driver if needed for compatibility

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older SSL protocols
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH security controls verified by the InSpec tests:
  - Ensure root login remains disabled
  - Maintain compliance with security standards (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests:
  - Challenge: InSpec has specific matchers and resource types that may not have direct equivalents in Ansible
  - Mitigation: Create custom Ansible modules or use community modules that provide similar functionality

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents:
  - Challenge: Chef Server provides organization management and role-based access control
  - Mitigation: Use AWX/Tower for RBAC and organization management, or implement custom solutions using Ansible inventory groups

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, convert to Ansible assertions or Molecule tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, convert to Ansible roles for infrastructure deployment

### Assumptions

1. The current setup uses Chef InSpec primarily for testing, not for continuous compliance monitoring
2. The deployment scripts are used for initial setup and not for ongoing management
3. There are no external Chef cookbooks or recipes being used that weren't included in the repository
4. The Ansible playbooks are already following best practices and don't require significant refactoring
5. There are no external dependencies on Chef-specific features that would be difficult to replicate in Ansible
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the environment and don't need to be replaced with CA-signed certificates
8. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives
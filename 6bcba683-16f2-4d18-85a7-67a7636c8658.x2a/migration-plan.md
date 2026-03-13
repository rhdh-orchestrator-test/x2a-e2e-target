# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: Security hardening for Apache SSL configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is or included as a template in Ansible.

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic infrastructure testing: Use the `ansible.builtin.assert` module with appropriate checks
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule for testing
  - Alternative: Use the Ansible `community.general.inspec` module to continue leveraging InSpec tests from within Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing, which provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2
- **SSH Hardening**: The SSH security controls from the InSpec profile need to be implemented as Ansible tasks and verified with appropriate tests
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider enhancing with Let's Encrypt integration for production environments
- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault or another secure secret management solution

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules and assertions
- **Chef Automate Deployment**: Converting the Chef Automate and Chef Server deployment scripts to Ansible will require understanding of the Chef deployment process and creating equivalent Ansible tasks
- **Test Framework Integration**: Ensuring that the new testing framework integrates smoothly with CI/CD pipelines that may have been using Test Kitchen

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These can remain largely unchanged as they are already in Ansible format
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing or integrate with the community.general.inspec module
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks with proper variable management and security considerations
4. **Test Framework** (kitchen.yml): Replace with Molecule configuration for testing the Ansible roles

### Assumptions

1. The repository is primarily used for demonstration purposes as indicated by the README.md mentioning "examples are companions to a Progress Chef white paper"
2. The existing Ansible playbooks are functional and do not require significant modifications
3. There are no additional Chef cookbooks or resources not visible in the current directory structure
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The migration does not need to preserve Chef Automate and Chef Infra Server functionality, but rather replace their deployment scripts with equivalent Ansible automation
6. No external dependencies or integrations beyond what is visible in the repository need to be considered
7. The security compliance requirements represented in the InSpec tests need to be maintained in the Ansible solution
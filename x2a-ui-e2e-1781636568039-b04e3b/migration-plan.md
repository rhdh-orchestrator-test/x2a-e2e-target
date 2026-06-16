# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** as most of the content is already in Ansible format, with the primary focus being on converting the InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents.

**Estimated Timeline**: 1-2 weeks for a complete migration, with the majority of time spent on test framework conversion and validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with HTTPS/SSL setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **inspec-website-tests**:
    - Description: InSpec tests for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for enterprise automation platform
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The current playbooks properly configure Apache with TLSv1.2 and disable insecure protocols. This should be maintained in the migrated solution.

- **SSH Security**: The InSpec profile checks for SSH root login restrictions. This should be incorporated into the Ansible playbooks as both a configuration and a verification step.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate/Infra Server deployment scripts need to be moved to Ansible Vault
  - Count: 1 set of credentials (username, password) in each deployment script

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions and may not have direct equivalents for all InSpec resources.
  - Mitigation: Consider using a hybrid approach where Ansible handles configuration and InSpec remains for testing, or invest in developing equivalent tests in Molecule/pytest-ansible.

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance reporting in the Ansible ecosystem.
  - Mitigation: Evaluate Ansible AWX/Tower with compliance add-ons or integrate with third-party compliance tools like OpenSCAP.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and incorporate best practices.

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks, replacing Chef Automate/Infra Server with appropriate Ansible-based alternatives.

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-compatible testing frameworks or integrate them into an Ansible workflow.

4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule or update to work with the new testing approach.

### Assumptions

1. The primary purpose of this repository is for demonstration/educational purposes rather than production use, based on the README content.

2. The InSpec tests are considered valuable and their functionality should be preserved in some form, not simply discarded.

3. A complete replacement for Chef Automate's compliance capabilities is desired, not just the configuration management aspects.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with proper secret management in the migrated solution.

6. The current Test Kitchen setup is used for testing and development, not for production deployments.
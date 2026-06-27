# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as we need to convert InSpec tests to Ansible-compatible testing frameworks. Estimated timeline: 1-2 weeks for a complete migration.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check, compliance with security standards (SRG-OS-000112)

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
- `index.html`: Simple HTML file used for testing web server deployment. Can be reused as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Convert InSpec tests to Ansible roles with appropriate checks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines (Jenkins, GitHub Actions, etc.)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for enterprise automation platform
  - GitLab/GitHub for code repository and CI/CD
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook specifically addresses SSL security. Ensure this security hardening is maintained in the migrated solution.
  - Migration approach: Convert to an Ansible role for Apache SSL hardening that can be reused across projects.

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH security configurations.
  - Migration approach: Create an Ansible role that both configures and verifies SSH security settings.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault.
  - SSL certificates are generated on the fly but should be managed securely in production.
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 3 credentials (username, password, organization name)
    - chef-server-deployment: 3 credentials (username, password, organization name)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Compliance Reporting**: If Chef InSpec was being used for compliance reporting, an alternative solution will be needed.
  - Mitigation: Investigate OpenSCAP integration with Ansible or Ansible Tower's compliance scanning capabilities.

- **Chef Automate Functionality**: If specific Chef Automate features were being used, equivalent functionality in Ansible Tower/AWX will need to be identified.
  - Mitigation: Document specific Chef Automate features in use and map to Ansible Tower/AWX features.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **website_https_verify.rb** (moderate complexity): Convert InSpec tests to Ansible assertions or Molecule tests
4. **ssh_profile.rb** (moderate complexity): Convert InSpec tests to Ansible assertions or Molecule tests
5. **chef-automate-deployment** and **chef-server-deployment** (high complexity): Replace with Ansible Tower/AWX deployment playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in production.
3. The self-signed certificates in the website_https.yml playbook would be replaced with proper certificates in production.
4. The Test Kitchen configuration is used for development and testing, not for production deployment.
5. The repository does not contain any custom Chef cookbooks or recipes that would need migration.
6. The SSH profile test is a standalone example and not part of a larger compliance framework.
7. The deployment scripts are meant for demonstration purposes and not for production use.
8. There are no external dependencies or integrations beyond what is explicitly defined in the files.
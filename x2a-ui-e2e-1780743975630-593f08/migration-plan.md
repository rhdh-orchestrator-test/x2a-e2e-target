# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns between the InSpec tests and Ansible playbooks.

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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used for testing web server functionality. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider Red Hat Insights or Ansible Automation Platform for enterprise compliance

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible-native solution.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbooks, which is a good practice to maintain

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks using Ansible's testing capabilities.
  - Mitigation: Use Ansible's assert module for basic checks and consider integrating with specialized tools for more complex compliance testing.

- **Chef Automate Deployment**: Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks will require understanding the installation process and dependencies.
  - Mitigation: Research Chef Automate installation requirements and create equivalent Ansible roles for deployment.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve idempotence and follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions, ensuring all compliance checks are preserved.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks, ensuring all configuration options are preserved.

4. **Testing Infrastructure**: Replace Test Kitchen with Molecule for testing Ansible roles and playbooks.

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while preserving the compliance checks.
2. The existing Ansible playbooks are functional and follow best practices.
3. The Chef Automate and Chef Infra Server deployment scripts are still relevant and needed in the migrated solution.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The repository is primarily used for demonstration purposes as indicated by the README.md, which mentions these are companion examples to a white paper.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the migrated solution.
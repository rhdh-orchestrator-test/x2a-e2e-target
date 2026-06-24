# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and straightforward nature of the components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration preserves the security hardening that disables SSLv3 and only enables TLSv1.2.
- **SSH Security**: The InSpec test verifies SSH root login is disabled. Ensure this security check is maintained in the Ansible-based testing.
- **Hardcoded Credentials**: The Chef server deployment scripts contain hardcoded credentials that should be replaced with Ansible Vault or another secure secret management solution:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the equivalent assertions and test structures.
  - Mitigation: Use Ansible's assert module for simple tests and consider Molecule for more complex testing scenarios.

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks will require understanding the equivalent Ansible modules and workflows.
  - Mitigation: Research Ansible modules for system configuration and package installation to replicate the Chef server deployment steps.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Review and update as needed for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing frameworks.
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks with proper secret management.
4. **Infrastructure Files** (kitchen.yml): Replace with Ansible-native testing framework configuration.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and do not need significant modifications.
2. The InSpec tests are currently used for compliance verification and need to be preserved in functionality, if not in form.
3. The Chef server deployment scripts are used for setting up development or testing environments and will need equivalent functionality in Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration does not need to preserve backward compatibility with Chef InSpec.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the migrated solution.
7. The repository is primarily for demonstration and educational purposes, as indicated by the README.md, rather than production use.
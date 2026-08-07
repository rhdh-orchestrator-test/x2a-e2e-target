# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the infrastructure code is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 2-3 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for web UI and job scheduling
  - Option 2: GitLab CI/CD for pipeline-based automation
  - Option 3: Jenkins with Ansible plugin

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are maintained in the migrated Ansible playbooks.
  - Migration approach: Preserve the SSL configuration in the Ansible tasks, ensuring TLS 1.2+ is enforced

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible task to enforce SSH configuration and use Ansible's assert module to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features.
  - Mitigation: Evaluate Ansible AWX/Tower or integrate with additional tools like Prometheus/Grafana for monitoring and compliance reporting.

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Convert InSpec tests to Ansible assertions

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Convert InSpec tests to Ansible assertions

3. **Chef Automate/Infra Server deployment scripts** (moderate complexity)
   - Create Ansible playbooks to replace the shell scripts
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is for demonstration and examples, not production use.
2. The InSpec tests are used for validation of configurations, not for continuous compliance monitoring.
3. There are no external dependencies on Chef Automate for reporting or compliance.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no complex data structures or custom Chef resources that would require special handling.
6. The repository does not contain actual Chef cookbooks, only InSpec tests and Ansible playbooks.
7. The migration will maintain the same functionality but standardize on Ansible as the single automation tool.
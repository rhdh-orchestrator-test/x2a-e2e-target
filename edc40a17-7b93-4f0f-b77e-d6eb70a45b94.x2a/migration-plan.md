# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a template for website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule for testing
  - **Option 2**: Use ansible-test framework
  - **Option 3**: Convert InSpec tests to Python-based tests using pytest

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Ansible collections for configuration management

### Security Considerations

- **SSL Configuration**: The current implementation hardens Apache against POODLE vulnerability. Ensure this security hardening is maintained in the Ansible migration.
- **SSH Hardening**: The SSH security profile checks for root login disablement. This should be incorporated into the Ansible security checks.
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials. These should be moved to Ansible Vault or another secrets management solution.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional scripting or use of specialized modules.
  - Mitigation: Use the `assert` module in Ansible to perform similar validation checks.

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated in Ansible.
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with tools like Ansible AWX/Tower for compliance dashboards.

- **Chef Automate Replacement**: Finding equivalent functionality for Chef Automate's compliance scanning and reporting.
  - Mitigation: Implement OpenSCAP with Ansible for compliance scanning or use commercial solutions like Ansible Tower with compliance plugins.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve idempotence and follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for deploying alternative solutions like AWX/Tower.

4. **Test Infrastructure** (kitchen.yml): Replace with Ansible Molecule for testing infrastructure.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and can be retained with minimal modifications.

3. There are no additional Chef cookbooks or resources beyond what is visible in the repository structure.

4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.

5. The deployment scripts are examples and not production-ready, given the hardcoded credentials.

6. The migration will focus on replacing Chef InSpec with Ansible-native testing while preserving the existing Ansible playbooks' functionality.

7. There are no external dependencies or integrations beyond what is explicitly mentioned in the files.
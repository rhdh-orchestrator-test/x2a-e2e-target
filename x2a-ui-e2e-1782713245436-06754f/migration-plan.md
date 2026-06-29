# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Replace InSpec tests with Ansible's built-in `assert` module or Ansible Molecule for testing
  - Convert InSpec resource tests to Ansible tasks with appropriate assertions
  - Consider using ansible-lint for static code analysis

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Molecule supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - Ansible AWX (open source) for web UI and REST API
  - GitLab CI/CD or GitHub Actions for pipeline integration

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced in the Apache configuration
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH security controls verified by the InSpec test
  - Ensure PermitRootLogin is properly configured in the migrated solution
  - Add additional SSH hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions
  - Mitigation: Use Ansible's assert module and register variables to perform similar checks
  - Consider implementing custom Ansible modules if needed for complex tests

- **Compliance Reporting**: InSpec provides structured compliance reporting
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with tools like Ansible Automation Platform

- **Certificate Management**: The current solution generates self-signed certificates
  - Mitigation: Use Ansible's crypto modules for certificate management or integrate with external certificate authorities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Update to current Ansible best practices
   - Refactor into roles for better organization
   - Replace deprecated syntax if any

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure equivalent coverage of security checks

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX
   - Create roles for system preparation and application deployment

### Assumptions

1. The primary goal is to move from a mixed Chef InSpec/Ansible environment to a pure Ansible solution
2. The existing Ansible playbooks are functional and can be used as a reference for the migration
3. The security compliance requirements will remain the same after migration
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. There is no external integration with other Chef products beyond what's in the repository
6. The self-signed certificates are acceptable for the environment (not production)
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only
8. The migration will include updating to current Ansible best practices and security standards
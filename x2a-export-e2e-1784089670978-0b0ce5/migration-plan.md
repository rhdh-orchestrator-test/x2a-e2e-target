# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Replace InSpec tests with Ansible's built-in `assert` module
  - Consider using Ansible Lint for static analysis
  - For more complex compliance testing, evaluate using Ansible's `community.general.xml` module or OpenSCAP integration

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `ansible-test` for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Disabling of vulnerable SSL protocols (as in poodle_fix.yml)
  - Proper certificate generation and management
  - Secure virtual host configuration

- **SSH Security**: The SSH compliance profile checks for secure SSH configuration. Migration should:
  - Implement equivalent checks using Ansible's assert module
  - Ensure SSH root login remains disabled

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions will require careful mapping of test logic
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using Ansible's `uri` module to replace HTTP/HTTPS checks

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Evaluate using Ansible callback plugins to generate compliance reports
  - Consider integrating with tools like OpenSCAP for more comprehensive compliance reporting

- **Chef Automate Functionality**: Chef Automate provides features that need Ansible equivalents
  - Mitigation: Map Chef Automate features to Ansible Automation Platform capabilities
  - Develop custom reporting solutions if needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Update to modern Ansible best practices
   - Implement idempotency improvements
   - Add documentation

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Convert to Ansible roles for infrastructure deployment
   - Implement Ansible Vault for credential management
   - Create equivalent user and organization management in Ansible Automation Platform

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Highest complexity
   - Convert to Ansible assertions or custom modules
   - Implement equivalent compliance reporting
   - Integrate with CI/CD pipeline

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining compliance testing capabilities
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. The deployment scripts are used for setting up test environments rather than production systems
4. No external data sources or databases are involved in the current setup
5. The security compliance requirements (SRG-OS-000112, etc.) will remain the same
6. The team has experience with both Chef and Ansible
7. No custom Chef resources or complex Chef-specific logic is present
8. The migration will include updating to current Ansible best practices
9. Test Kitchen is only used for development/testing, not for production deployments
10. The hardcoded credentials in the deployment scripts are for testing purposes only
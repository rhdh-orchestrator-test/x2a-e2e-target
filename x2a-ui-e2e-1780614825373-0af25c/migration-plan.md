# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

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
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Implement Ansible Molecule for comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set up equivalent monitoring and compliance solutions
  - Configure system requirements (sysctl settings)
  - Create users and organizations in the replacement system

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Consider adding more modern security headers
  - Implement proper certificate management

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure root login remains disabled in the migrated solution
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent test coverage.
  - Mitigation: Consider using Ansible's assert module with well-defined conditions that match InSpec's expectations.

- **Chef Server Replacement**: If Chef Server functionality is needed, determine appropriate Ansible alternatives:
  - Mitigation: Consider AWX/Ansible Tower for web UI and role-based access control, or use GitOps approaches with CI/CD pipelines.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; may need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity to convert to Ansible testing framework.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity as they require replacing Chef-specific functionality with Ansible equivalents.

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use.
2. The InSpec tests are intended to validate the configurations applied by the Ansible playbooks.
3. There is no actual dependency on Chef Infra for configuration management, only on InSpec for testing.
4. The deployment scripts are used for setting up test environments rather than production systems.
5. There are no external dependencies or integrations not visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
7. The migration will maintain the same level of security compliance checking currently provided by InSpec.
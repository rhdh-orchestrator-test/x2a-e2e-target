# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec profiles and Ansible playbooks that are used together to implement and verify compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Based on the repository analysis, this is a low-complexity migration that should take approximately 1-2 weeks to complete, with the primary focus on:
1. Converting InSpec tests to Ansible-compatible testing frameworks (like Molecule with TestInfra)
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Ensuring the integration between Ansible playbooks and compliance testing remains intact

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing Test Kitchen with Ansible Molecule for testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with TestInfra for infrastructure testing
  - Option 2: Use Ansible assert modules directly in playbooks for simple tests
  - Option 3: Use the ansible-test framework for more complex testing scenarios

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - Ansible Collections for configuration management
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL security configurations in the Apache web server, particularly the TLS protocol settings that mitigate the POODLE vulnerability.
  - Migration approach: Convert the SSL configuration to use the Ansible `apache2_module` and `apache2_conf` modules

- **SSH Security**: The SSH security profile tests must be preserved to ensure SSH root login remains disabled.
  - Migration approach: Convert InSpec tests to TestInfra or Ansible assert modules

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely using Ansible Vault or external certificate management
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance validation.
  - Mitigation: Use Ansible Molecule with TestInfra which provides similar testing capabilities to InSpec

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance reporting in the Ansible ecosystem.
  - Mitigation: Consider implementing Ansible AWX/Tower with compliance reporting plugins or integrating with third-party compliance tools

- **Test Kitchen Integration**: Replacing Test Kitchen's integration with both Ansible and InSpec.
  - Mitigation: Implement Ansible Molecule which provides similar functionality for testing Ansible roles

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as these are already in Ansible format and can be preserved with minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing frameworks
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as these need to be completely rewritten as Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md
2. The target environment is Ubuntu 20.04 as specified in kitchen.yml
3. The deployment scripts are intended for on-premises or generic cloud VM deployment
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The repository is used for educational/demonstration purposes rather than production deployment
6. The migration will maintain the same level of compliance validation currently provided by InSpec
7. The existing Ansible playbooks are functional and follow best practices
8. There are no external dependencies or integrations not visible in the repository
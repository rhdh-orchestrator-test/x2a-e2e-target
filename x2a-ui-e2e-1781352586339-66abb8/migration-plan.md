# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server. Can be preserved as-is or included in Ansible content.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing
  - Alternatively, use Ansible assert modules for inline testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to an Ansible task or Molecule test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Test Conversion**: Converting Chef InSpec tests to Ansible-native testing requires understanding both testing frameworks
  - Mitigation: Use Ansible assert modules for simple tests and Molecule for more complex scenarios

- **Compliance Testing**: Ensuring the same level of compliance testing without InSpec
  - Mitigation: Consider using ansible-lint with custom rules or maintaining a separate compliance testing framework

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Research existing Ansible roles for Chef server deployment or create custom roles

### Migration Order

1. Convert InSpec tests to Ansible Molecule tests (low risk, preserves testing capability)
2. Replace Test Kitchen with Ansible Molecule (moderate complexity)
3. Convert Chef server deployment scripts to Ansible playbooks (higher complexity)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be preserved as-is
2. The target environment will continue to be Ubuntu 20.04
3. The deployment of Chef Automate and Chef Infra Server is still required (rather than being replaced entirely)
4. The security compliance requirements remain the same
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration is primarily focused on replacing Chef InSpec with Ansible-native testing
7. No database or complex application dependencies are present
8. The repository is primarily for demonstration purposes rather than production use
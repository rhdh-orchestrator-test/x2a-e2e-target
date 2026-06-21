# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most of the Ansible components already in place. The migration will primarily involve:

1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained in the new implementation

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
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
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM targets

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for enterprise automation platform
  - GitLab CI/CD or Jenkins for pipeline automation

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older SSL/TLS protocols
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH root login compliance check must be preserved:
  - Implement equivalent checks using Ansible's assert module or Molecule
  - Ensure the SSH configuration is properly managed in the migrated solution

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Self-signed certificates generated in website_https.yml

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent coverage.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and develop reusable test patterns.

- **Chef Automate Functionality**: Chef Automate provides compliance reporting that needs an equivalent in the Ansible ecosystem.
  - Mitigation: Evaluate Ansible Tower/AWX compliance capabilities or integrate with additional tools like OpenSCAP.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize existing Ansible playbooks
   - Ensure idempotence and best practices

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   - Validate equivalent coverage

3. **Chef Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Replace Chef Automate/Infra Server with appropriate Ansible-based solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
3. The self-signed certificates are acceptable for the intended use case.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.
6. The compliance tests are focused on HTTPS and SSH configurations only.
7. The deployment scripts are intended for standalone environments rather than distributed systems.
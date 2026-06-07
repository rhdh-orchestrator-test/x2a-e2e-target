# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Server deployment scripts to Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance with specific tags (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed, can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider integrating with other compliance tools like OSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Use Ansible's crypto modules and maintain the same security settings

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with specialized compliance tools for more complex requirements.

- **Chef Automate/Server Deployment**: Converting bash scripts to idempotent Ansible playbooks.
  - Mitigation: Break down the scripts into logical tasks and use Ansible's idempotent modules instead of direct commands.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Implement proper variable handling and templating

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Consider merging with website_https as a role

3. **Chef Automate/Server deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

4. **InSpec tests** (high complexity)
   - Convert to Ansible-native testing solutions
   - Ensure compliance requirements are maintained

### Assumptions

1. The primary goal is to fully migrate to Ansible, eliminating dependencies on Chef InSpec and other Chef components.
2. The existing Ansible playbooks are functional but may need refactoring to follow best practices.
3. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests need to be maintained in the Ansible solution.
4. The deployment scripts contain hardcoded credentials that should be secured in the migration.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The migration will maintain the same functionality for web server deployment and compliance checking.
7. There may be additional Chef components or dependencies not visible in the provided files that could impact the migration.
8. The Test Kitchen configuration suggests this is a development/testing environment rather than production.
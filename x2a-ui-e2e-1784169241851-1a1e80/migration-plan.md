# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with the majority of time spent on converting InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

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
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be retained as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using the community.general.test_module for more complex assertions

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system parameters (hostname, sysctl)
  - Install and configure equivalent monitoring/compliance solutions (options include AWX/Tower, Prometheus with Grafana, or ELK stack)

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables SSLv3. This should be maintained or enhanced in the Ansible migration.
  - Migration approach: Use the same Apache configuration but implement it via Ansible's template module instead of the replace module.

- **SSH Security**: The InSpec test checks for disabled root login. This security check should be maintained.
  - Migration approach: Create an Ansible playbook that both configures SSH properly and verifies the configuration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Use Ansible's assert module with carefully constructed conditions to match InSpec's behavior.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may be difficult to replicate in pure Ansible.
  - Mitigation: Consider integrating with additional tools like Ansible Tower/AWX for reporting or maintaining InSpec just for testing while using Ansible for configuration.

- **Chef Server Functionality**: If the environment relies on Chef Server features, equivalent functionality needs to be implemented in Ansible.
  - Mitigation: Evaluate which Chef Server features are actually being used and implement them using Ansible roles, collections, and potentially AWX/Tower.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already in Ansible, no migration needed)
2. **InSpec Tests** (convert to Ansible assertions or Molecule tests)
3. **Chef Deployment Scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible, rather than being a production deployment.
2. The hardcoded credentials in the deployment scripts are examples and not used in production.
3. The self-signed certificates are for testing purposes only.
4. There are no additional Chef cookbooks or resources being used beyond what's visible in the repository.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The deployment scripts are intended for single-server deployments rather than distributed systems.
7. There are no external dependencies or integrations beyond what's explicitly referenced in the code.
# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to convert. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the website
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Replace with Ansible Lint or Ansible Molecule
  - For infrastructure validation: Replace with Ansible assert modules or custom modules
  - For security scanning: Consider integrating OpenSCAP with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that either:
  - Deploy an alternative compliance solution like OpenSCAP
  - Or set up Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced
  - Maintain the disabling of vulnerable protocols (SSLv3)
  - Consider updating to more modern cipher suites

- **SSH Security**: The InSpec tests verify SSH security configurations. Migration should:
  - Implement equivalent checks using Ansible
  - Ensure root login remains disabled
  - Maintain compliance with security standards referenced in the InSpec tests (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate deployment scripts (username, password)
  - Self-signed certificates generated in the Ansible playbook
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Use Ansible's assert module for validation checks

- **Compliance Reporting**: InSpec provides structured compliance reporting that needs to be replicated.
  - Mitigation: Consider using Ansible callback plugins to generate compliance reports
  - Alternatively, integrate with tools like OpenSCAP that can provide similar reporting

- **Chef Automate Functionality**: If Chef Automate is being used for compliance scanning and reporting, equivalent functionality needs to be established.
  - Mitigation: Evaluate Ansible AWX/Tower with compliance scanning plugins

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, minimal changes needed
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, minimal changes needed
3. **InSpec Tests** (Priority 2): Convert to Ansible assertions or Molecule tests
4. **Chef Deployment Scripts** (Priority 3): Replace with Ansible playbooks for alternative solutions

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for validation and compliance checking, not for continuous monitoring
3. There are no external dependencies on Chef Automate for reporting or dashboards
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. There is no requirement to maintain backward compatibility with Chef InSpec
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
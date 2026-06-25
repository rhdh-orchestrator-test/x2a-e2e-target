# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as the repository already contains Ansible playbooks. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions like Ansible Molecule with testinfra or other compatible testing frameworks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities (POODLE) in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for lightweight testing
  - Option 3: Ansible Molecule with Ansible's assert module for basic testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule provides similar functionality for provisioning, converging, verifying, and destroying test instances

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH security controls from the InSpec profile
  - Ensure root login remains disabled
  - Consider adding more SSH hardening measures from modern security benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates generated in the website_https.yml playbook
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use testinfra with Python for more complex tests, Ansible assert for simpler tests

- **Test Kitchen to Molecule**: Adapting test workflows to use Molecule instead of Test Kitchen
  - Challenge: Different configuration syntax and workflow
  - Mitigation: Create Molecule scenarios that mirror the existing Test Kitchen configuration

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible playbooks
  - Challenge: Understanding Chef Automate deployment requirements
  - Mitigation: Create Ansible roles for Chef Automate deployment or consider migrating to Ansible Tower/AWX

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already Ansible)
   - Review and update as needed to current Ansible best practices
   - Consider combining into a single role with separate tasks

2. **InSpec Tests** (moderate complexity)
   - Create equivalent tests using Ansible Molecule with testinfra
   - Ensure all compliance checks are maintained

3. **Chef Automate Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't need significant modifications
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The deployment environment will remain similar (Ubuntu 20.04 on Vagrant VMs)
5. There are no external dependencies or integrations not visible in the provided files
6. The Chef Automate and Chef Server deployment may be optional in the future Ansible-only workflow
7. No custom InSpec resources are being used beyond what's visible in the provided tests
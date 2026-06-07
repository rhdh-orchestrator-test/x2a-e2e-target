# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

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
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page. No migration considerations needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's built-in assert module for basic tests
  - Option 2: Use Molecule with testinfra for more comprehensive testing
  - Option 3: Maintain InSpec as a standalone testing tool but invoke from Ansible

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Vagrant (latest)**: Can be maintained for local testing or replaced with containerized testing using Docker with Molecule

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains or improves the security posture:
  - Maintain TLSv1.2 requirement and disable older protocols
  - Consider upgrading to include TLSv1.3 support
  - Ensure proper certificate handling

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled in migrated configurations
  - Maintain compliance with referenced security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates in the website_https.yml playbook should use Ansible Vault or a proper certificate management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules:
  - Challenge: InSpec's declarative testing style differs from Ansible's procedural approach
  - Mitigation: Use Ansible assert module with appropriate conditionals or maintain InSpec as a separate tool called from Ansible

- **Test Kitchen to Molecule**: Transitioning test frameworks:
  - Challenge: Different configuration formats and testing approaches
  - Mitigation: Create equivalent Molecule scenarios for each Test Kitchen suite

- **Chef Automate Deployment**: The bash scripts for Chef Automate deployment need to be converted to Ansible:
  - Challenge: Ensuring idempotent execution of Chef server setup
  - Mitigation: Use Ansible's command/shell modules with creates/changed_when to ensure idempotence

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **Chef Automate deployment scripts** (moderate complexity, convert bash to Ansible tasks)
4. **InSpec tests** (high complexity, requires testing framework decisions)

### Assumptions

1. The current setup uses Test Kitchen to provision a Vagrant VM, run Ansible playbooks, and verify with InSpec tests.
2. The repository is primarily for demonstration purposes rather than production use.
3. The Chef InSpec tests are used for compliance verification only, not for remediation.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced in a production environment.
5. The target environment for the migrated solution will continue to be Ubuntu 20.04 or compatible systems.
6. The migration will maintain the same level of security compliance as demonstrated in the InSpec tests.
7. There are no external dependencies or integrations beyond what is visible in the repository.
# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

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
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security tagging (STIG, CCI references)

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Install and configure equivalent monitoring/compliance solutions (options include AWX/Tower, Prometheus, Grafana)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Create an Ansible role for Apache SSL hardening that applies the same configuration

- **SSH Security**: The SSH root login check must be maintained
  - Migration approach: Convert the InSpec control to an Ansible task using the lineinfile or template module to ensure proper SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
    - Migration approach: Use Ansible Vault to secure these credentials

- **Self-signed certificates**: The current solution generates self-signed certificates
  - Migration approach: Create an Ansible role for certificate management, potentially integrating with Let's Encrypt for production environments

### Technical Challenges

- **Compliance Reporting**: Chef InSpec provides detailed compliance reporting that needs to be replicated
  - Mitigation: Investigate Ansible callback plugins or integration with tools like OpenSCAP to generate compliance reports

- **Test Conversion**: Converting InSpec tests to Ansible assertions requires careful mapping of test logic
  - Mitigation: Create a test conversion guide and validate each converted test thoroughly

- **Deployment Script Logic**: The Chef deployment scripts contain specific configuration steps that need to be accurately replicated
  - Mitigation: Break down the script into discrete tasks and create equivalent Ansible tasks for each step

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Integrate with the website_https role

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.

2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already working correctly and don't require functional changes.

3. There are no external dependencies or integrations beyond what's visible in the repository.

4. The deployment scripts are examples and not used in production environments (they contain hardcoded credentials).

5. The target environment will continue to be Ubuntu 20.04 or compatible systems.

6. The migration doesn't need to maintain backward compatibility with Chef InSpec.

7. The security compliance requirements (STIG, CCI references) need to be maintained in the Ansible solution.
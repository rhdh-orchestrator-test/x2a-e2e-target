# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

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
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with pytest-ansible for more complex testing scenarios

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use simple Vagrant or Docker-based testing workflows managed by Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to Ansible Automation Platform (formerly Ansible Tower)
  - Option 2: Use AWX (open-source version of Ansible Tower)
  - Option 3: Use GitLab CI/CD or Jenkins with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration parameters but use Ansible's native modules

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verify steps

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks.
  - Mitigation: Use Ansible assert modules or Molecule verify steps to replicate InSpec tests.

- **Chef Automate Deployment**: Replacing Chef Automate deployment with Ansible Automation Platform.
  - Mitigation: Create Ansible playbooks to deploy Ansible Automation Platform or AWX.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
3. **Chef deployment scripts** (high complexity, requires complete replacement with Ansible Automation Platform deployment)

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining the same level of compliance verification.
2. The existing Ansible playbooks can be reused with minimal modifications.
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible Automation Platform deployment.
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs.
5. No external dependencies or complex integrations exist beyond what is visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution.
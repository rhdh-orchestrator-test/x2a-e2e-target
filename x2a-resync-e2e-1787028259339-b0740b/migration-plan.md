# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. There are also shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, and SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH server configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Verifies SSH root login is disabled according to security standards

- **automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Configures hostname, system parameters, and installs Chef Automate with Infra Server

- **chef-server-deploy**:
    - Description: Bash script that deploys only Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Configures hostname, system parameters, and installs Chef Infra Server

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Static HTML file for the website. Can be directly included in the Ansible project.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider using OpenSCAP with Ansible or Ansible Lint with custom rules

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: If these are only for demonstration purposes, consider replacing with:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration maintains or improves the security posture:
  - Update SSL/TLS configurations to current best practices
  - Consider using Let's Encrypt integration instead of self-signed certificates
  - Implement proper certificate management

- **SSH Hardening**: The InSpec tests check for SSH security. Ensure these checks are maintained:
  - Convert the SSH compliance checks to Ansible pre/post tasks or separate playbooks
  - Consider using the `ansible-lockdown` collection for standardized security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible's assertion modules or external testing tools
  - Ensuring the same level of reporting and documentation

- **Bash Script Conversion**: The Chef deployment scripts need to be converted to Ansible playbooks:
  - Research Ansible modules for system configuration (hostname, sysctl)
  - Determine if Chef Automate/Infra Server is still needed or can be replaced with Ansible tooling

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need restructuring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires converting to Ansible-native testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires architectural decisions about replacing Chef infrastructure

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can be used alongside Ansible.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. There is no actual production deployment dependent on these scripts.
4. The hardcoded credentials in the deployment scripts are for demonstration only.
5. The migration goal is to use pure Ansible without Chef components.
6. The compliance requirements in the InSpec tests need to be preserved in the Ansible solution.
7. Test Kitchen is only used for development/testing and not for production deployments.
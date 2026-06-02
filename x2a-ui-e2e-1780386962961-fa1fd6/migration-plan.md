# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with the primary focus being on consolidating the existing Ansible playbooks and Chef InSpec tests into a pure Ansible solution. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for integration testing
  - Use Ansible's `assert` module for runtime validation
  - Consider Molecule for Ansible role testing
  - Alternatively, maintain InSpec tests but run them from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Simple Vagrant or Docker-based testing scripts

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in the Apache configuration

- **SSH Security**: The SSH security checks in ssh_profile.rb need to be preserved
  - Implement equivalent checks using Ansible's assert module or maintain as InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible equivalents requires careful mapping of test assertions
  - Mitigation: Consider using Ansible's assert module with appropriate conditionals or maintain InSpec as a testing tool called from Ansible

- **Chef Automate/Server Deployment**: Replacing the Chef deployment scripts with Ansible equivalents
  - Mitigation: Research Ansible roles for Chef deployment or create custom roles based on the installation steps in the bash scripts

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and improve variable naming

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https.yml as they're related

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or maintain as InSpec tests called from Ansible

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts for Chef Automate and Chef Server deployment

### Assumptions

1. The repository is primarily a demonstration of using Chef InSpec with Ansible rather than a production deployment
2. The target environment is Ubuntu 20.04 as specified in kitchen.yml
3. The deployment is intended for testing/lab environments given the hardcoded credentials
4. The primary goal is to consolidate on Ansible while maintaining the same security validation capabilities
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The Chef deployment scripts are intended for on-premises or cloud VM deployment
7. The security tests are based on standard compliance frameworks (STIG is referenced)
8. No database or complex application dependencies are present
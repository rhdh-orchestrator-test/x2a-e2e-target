# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be primarily focused on examples and demonstrations rather than production infrastructure code. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Consider using ansible-lint for static analysis
  - Option 4: For organizations committed to InSpec, continue using InSpec with Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Consider GitHub Actions or other CI/CD tools for automated testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLS 1.2 is enforced and SSL3 is disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH compliance checks in ssh_profile.rb need to be implemented in Ansible
  - Create equivalent checks using Ansible's assert module or Molecule verifiers

- **Vault/secrets management**:
  - The current repository contains hardcoded credentials in the deploy scripts (username, password)
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider maintaining InSpec tests alongside Ansible if the organization is already invested in InSpec

- **Chef Automate/Server Deployment**: The deployment scripts for Chef infrastructure will need complete rethinking
  - Mitigation: Determine if Chef infrastructure is still needed or if it can be replaced with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add proper variable handling and improve security practices

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https.yml as they are related

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-native testing or Molecule
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If needed, create Ansible playbooks to deploy Chef components
   - If not needed, create equivalent Ansible Tower/AWX setup

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The organization is moving from a mixed Chef/Ansible environment to an Ansible-only environment
3. Compliance testing is an important aspect that needs to be maintained in the migration
4. The Chef Automate and Chef Server deployment scripts may or may not be needed in the new environment
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The organization has not heavily invested in Chef-specific tooling beyond what's shown in this repository
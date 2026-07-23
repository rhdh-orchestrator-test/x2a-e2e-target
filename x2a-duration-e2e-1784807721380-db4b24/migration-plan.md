# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure deployment. The migration scope is relatively small, focusing on:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Two Chef InSpec test profiles for verifying HTTPS configuration and SSH security
3. Two bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main focus will be on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

- **website-https-verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Static HTML file used in the website deployment. Can be preserved as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality to Test Kitchen but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create roles for Chef server deployment
  - Use Ansible Vault for credential management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security hardening measures are preserved in the migrated solution:
  - Disabling SSLv3 (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - Self-signed certificate generation

- **SSH Hardening**: The SSH InSpec profile checks for root login restrictions. Ensure this security check is implemented in the Ansible equivalent:
  - Create an Ansible task to verify SSH configuration
  - Implement remediation tasks to fix non-compliant configurations

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions:
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible's assert module with appropriate conditions or integrate with specialized testing tools

- **Deployment Script Conversion**: Converting bash scripts to idempotent Ansible playbooks:
  - Challenge: Ensuring proper error handling and idempotency
  - Mitigation: Use Ansible's command/shell modules with appropriate changed_when and failed_when conditions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and comments
   - Implement idempotency improvements if needed

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved
   - Validate against the same targets

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles and playbooks
   - Implement proper variable management with Ansible Vault
   - Test deployment in isolated environment

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The InSpec tests are used for compliance verification of infrastructure deployed by the Ansible playbooks, forming a hybrid Chef/Ansible workflow.

3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely with Ansible-based solutions.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. There are no external dependencies or integrations beyond what's visible in the repository.

6. The migration will preserve the functionality of the existing solution while standardizing on Ansible as the single automation tool.
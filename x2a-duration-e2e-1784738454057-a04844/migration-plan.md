# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used together for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be replaced with Ansible-based deployment solutions.

Based on the repository analysis, this is a low-complexity migration that should take approximately 1-2 weeks to complete, with the primary focus being on replacing InSpec tests with equivalent Ansible testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

After thorough analysis using file_search for Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), and PowerShell modules (.psd1), no traditional infrastructure-as-code modules were found in this repository. The repository contains:

- Ansible playbooks (.yml files)
- Chef InSpec test files (.rb files)
- Bash scripts for Chef Automate and Chef Infra Server deployment

The following components require migration planning:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate deployment, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing solutions.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions such as:
  - Molecule for infrastructure testing
  - ansible-lint for static code analysis
  - testinfra for Python-based infrastructure testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like:
  - AWX (open-source version of Ansible Tower)
  - Semaphore (lightweight alternative)

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (currently done in poodle_fix.yml)
  - Consider adding support for TLSv1.3
  - Maintain the self-signed certificate generation or provide options for Let's Encrypt integration

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Preserve this security check in the new testing framework
  - Consider expanding SSH hardening to include additional best practices

- **Vault/secrets management**:
  - No explicit secrets management was detected in the repository
  - Hardcoded credentials were found in the Chef server setup scripts (username, password)
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to an Ansible-native testing solution will require:
  - Understanding the InSpec resource model and finding equivalent testinfra or Molecule verifiers
  - Ensuring the same level of compliance validation is maintained
  - Solution: Create a mapping of InSpec resources to testinfra/Molecule equivalents

- **Deployment Script Conversion**: Converting the Chef Automate/Infra Server deployment scripts to Ansible:
  - Challenge: Ensuring idempotent installation and configuration
  - Solution: Create Ansible roles for Chef Automate and Chef Infra Server deployment

### Migration Order

1. Convert InSpec tests to Ansible-native testing solutions (low risk, foundation for further work)
   - ssh_profile.rb → testinfra or Molecule verifier
   - website_https_verify.rb → testinfra or Molecule verifier

2. Update Test Kitchen configuration to use Molecule (moderate complexity)
   - Replace kitchen.yml with molecule.yml and associated configuration

3. Convert Chef server deployment scripts to Ansible playbooks (higher complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential storage

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require modification beyond testing framework changes.

2. The primary goal is to eliminate Chef InSpec dependencies while maintaining the same level of compliance validation.

3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments and not production systems.

4. The repository is primarily used for demonstration purposes related to the white paper mentioned in the README.md.

5. No external dependencies or integrations beyond what's visible in the repository need to be considered.

6. The migration will maintain compatibility with Ubuntu 20.04 as the target platform.
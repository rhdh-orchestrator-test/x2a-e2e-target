# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance testing

- **chef-automate-deploy**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `chef-and-ansible/index.html`: Sample HTML file used for testing - can be incorporated into Ansible as a template

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Test for playbook verification
  - Option 3: Continue using InSpec but integrate with Ansible workflow

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-compatible CI/CD pipeline configuration

- **Chef Automate/Chef Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure setup
  - Consider migrating to Ansible Automation Platform if enterprise features are needed

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the POODLE fix playbook
  - Ensure TLS 1.2 is enforced and SSL3 is disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH compliance profile must be converted to equivalent Ansible checks
  - Maintain the security control for disabling root login
  - Preserve compliance metadata (CCI IDs, STIG IDs, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework while maintaining the same level of compliance validation
  - Mitigation: Use testinfra with Molecule which provides similar testing capabilities

- **Compliance Metadata**: Preserving compliance metadata (CCI IDs, STIG IDs) when migrating from InSpec to Ansible-native testing
  - Mitigation: Document compliance mappings in Ansible playbook comments or separate documentation

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality
  - Mitigation: Consider if Chef Server is still needed or if Ansible can fully replace its functionality

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbook
   - Add documentation and improve variable naming

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https playbook as a role

3. **InSpec tests** (moderate complexity)
   - Convert to Molecule with testinfra or other Ansible-compatible testing framework
   - Ensure all compliance checks are preserved

4. **Chef Automate/Server deployment scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault
   - Consider if Chef Automate/Server is still needed or can be replaced with Ansible Automation Platform

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The Chef Automate and Chef Server deployment is for demonstration purposes and not critical production infrastructure
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data handling or state management requirements
7. The security compliance requirements (STIG, CCI) need to be preserved in the migrated solution
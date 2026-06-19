# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing where needed

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for CI/CD pipelines
  - Ansible Collections for configuration management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLS 1.2 remains enforced
  - Consider updating to also include TLS 1.3 support

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be preserved
  - Convert InSpec controls to Ansible assert statements or Molecule verifiers
  - Maintain compliance with security standards (SRG-OS-000112, CCI-000774)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - website_https module: 0 hardcoded credentials
    - poodle_fix module: 0 hardcoded credentials
    - chef-automate-deployment module: 1 hardcoded password
    - chef-server-deployment module: 1 hardcoded password

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires careful mapping of assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions
  - Use Ansible's assert module and Molecule verifiers to replicate InSpec functionality

- **Chef Automate Functionality**: Replacing Chef Automate's compliance scanning capabilities
  - Mitigation: Evaluate OpenSCAP with Ansible for compliance scanning
  - Consider commercial solutions like Tenable or Qualys if advanced compliance reporting is needed

- **Maintaining Compliance Standards**: Ensuring the migrated solution still meets compliance requirements
  - Mitigation: Document how each compliance control is addressed in the new Ansible solution
  - Create a traceability matrix from original InSpec controls to new Ansible tests

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already Ansible)
   - Review and update as needed to current Ansible best practices
   - No actual migration needed, just potential modernization

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Molecule tests
   - Convert ssh_profile.rb to Molecule tests
   - Validate that new tests provide equivalent coverage

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential management
   - Test deployment in isolated environment

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are meant to validate the Ansible configurations, not to be run independently
3. The deployment scripts are templates that would be customized for actual deployments
4. No external data sources or databases are being used
5. No complex orchestration or scheduling is required
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There are no specific performance requirements for the migrated solution
8. The security standards referenced (SRG, CCI) need to be maintained in the migrated solution
9. No specific backup or disaster recovery requirements are defined
10. The migration does not need to preserve backward compatibility with Chef InSpec
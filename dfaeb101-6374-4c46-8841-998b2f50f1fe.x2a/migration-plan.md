# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates POODLE SSL vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-tests**:
    - Description: Chef InSpec test profiles for verifying HTTPS website functionality, security, and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks, SSH security compliance

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
- `index.html`: Simple HTML file used as a template. Can be directly incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with OpenSCAP using the ansible-openscap module
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality specifically designed for Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate templates for SSL configuration

- **SSH Security**: The SSH compliance checks must be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely using ansible-vault encrypted variables

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing functionality currently provided by InSpec
  - Mitigation: Evaluate ansible-lint, OpenSCAP, or maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen to Molecule Migration**: Converting the test framework requires careful mapping of functionality
  - Mitigation: Create a Molecule scenario that replicates the current Test Kitchen setup

### Migration Order

1. **website-https-configuration** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Improve variable handling and templating

2. **poodle-ssl-fix** (low risk, already Ansible)
   - Integrate with the website-https role as a security enhancement option

3. **chef-deployment** (moderate complexity)
   - Convert shell scripts to Ansible roles for Chef infrastructure deployment
   - Implement proper secret management with Ansible Vault

4. **inspec-tests** (high complexity)
   - Decide on compliance testing strategy (ansible-lint, OpenSCAP, or InSpec)
   - Implement equivalent tests in the chosen framework

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the compliance testing capabilities
2. The InSpec tests are valuable and need to be preserved in some form
3. The deployment scripts for Chef infrastructure are still needed (not being replaced by other tools)
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data handling or state management requirements
8. No specific performance requirements for the deployment scripts